# -*- coding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.core import paginator
from django.db import connection
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, Context, RequestContext
from django.utils.translation import ugettext as _

from helpdesk.forms import TicketForm, UserSettingsForm, EmailIgnoreForm, EditTicketForm, TicketCCForm, TicketTypeForm, FollowUpForm, AssignToForm, FilterForm
from helpdesk.lib import send_templated_mail, line_chart, bar_chart, query_to_dict, apply_query, safe_template_context
from helpdesk.models import Ticket, Queue, FollowUp, TicketChange, PreSetReply, Attachment, SavedSearch, IgnoreEmail, TicketCC
from helpdesk.settings import HAS_TAG_SUPPORT
  
from django_tables2_reports.config import RequestConfigReport as RequestConfig
from django_tables2_reports.utils import create_report_http_response

if HAS_TAG_SUPPORT:
    from tagging.models import Tag, TaggedItem

from helpdesk.tables import TicketTable, UnassignedTicketTable, UnpagedTicketTable
staff_member_required = user_passes_test(lambda u: u.is_authenticated() and u.is_active and u.is_staff)
superuser_required = user_passes_test(lambda u: u.is_authenticated() and u.is_active and u.is_superuser)
from billservice.helpers import systemuser_required
from billservice.models import Account
from ebscab.lib.decorators import render_to, ajax_request
from django.contrib import messages
from django.utils.safestring import mark_safe

import cPickle, pickle
from helpdesk.lib import b64decode, b64encode
        
from object_log.models import LogItem
log = LogItem.objects.log_action


def dashboard(request):
    """
    A quick summary overview for users: A list of their own tickets, a table
    showing ticket counts by queue/status, and a list of unassigned tickets
    with options for them to 'Take' ownership of said tickets.
    """

    tickets = Ticket.objects.filter(
            assigned_to=request.user,
        ).exclude(
            status=Ticket.CLOSED_STATUS,
        )

    ticket_table = UnpagedTicketTable(tickets)
    table_to_report = RequestConfig(request, paginate=False ).configure(ticket_table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
            
    unassigned_tickets = Ticket.objects.filter(
            assigned_to__isnull=True,
        ).exclude(
            status=Ticket.CLOSED_STATUS,
        )

    
    unassigned_ticket_table = UnassignedTicketTable(unassigned_tickets)
    table_to_report = RequestConfig(request, paginate=False ).configure(unassigned_ticket_table)
    if table_to_report:
        return create_report_http_response(table_to_report, request)
    # The following query builds a grid of queues & ticket statuses,
    # to be displayed to the user. EG:
    #          Open  Resolved
    # Queue 1    10     4
    # Queue 2     4    12

    cursor = connection.cursor()
    cursor.execute("""
        SELECT      q.id as queue,
                    q.title AS name,
                    COUNT(CASE t.status WHEN '1' THEN t.id WHEN '2' THEN t.id END) AS open,
                    COUNT(CASE t.status WHEN '3' THEN t.id END) AS resolved
            FROM    helpdesk_ticket t,
                    helpdesk_queue q
            WHERE   q.id =  t.queue_id
            GROUP BY queue, name
            ORDER BY q.id;
    """)
    dash_tickets = query_to_dict(cursor.fetchall(), cursor.description)

    return render_to_response('helpdesk/dashboard.html',
        RequestContext(request, {
            'user_tickets': tickets,
            'unassigned_tickets': unassigned_tickets,
            'dash_tickets': dash_tickets,
            'ticket_table': ticket_table,
            'unassigned_ticket_table': unassigned_ticket_table
        }))
dashboard = staff_member_required(dashboard)


def delete_ticket(request, ticket_id):
    if  not (request.user.account.has_perm('helpdesk.delete_ticket')):
        messages.error(request, _(u'У вас нет прав на удаление заявок'), extra_tags='alert-danger')
        return HttpResponseRedirect(request.path)
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'GET':
        return render_to_response('helpdesk/delete_ticket.html',
            RequestContext(request, {
                'ticket': ticket,
            }))
    else:
        ticket.delete()
        return HttpResponseRedirect(reverse('helpdesk_home'))
delete_ticket = staff_member_required(delete_ticket)


def view_ticket(request, ticket_id):
    if  not (request.user.account.has_perm('helpdesk.view_ticket')):
        messages.error(request, _(u'У вас нет прав на просмотр заявок'), extra_tags='alert-danger')
        return HttpResponseRedirect(request.path)
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.GET.has_key('take'):
        # Allow the user to assign the ticket to themselves whilst viewing it.
        ticket.assigned_to = request.user.account
        ticket.save()

    if request.GET.has_key('close') and ticket.status == Ticket.RESOLVED_STATUS:
        if not ticket.assigned_to:
            owner = 0
        else:
            owner = ticket.assigned_to.id

        # Trick the update_ticket() view into thinking it's being called with
        # a valid POST.
        request.POST = {
            'new_status': Ticket.CLOSED_STATUS,
            'public': 1,
            'owner': owner,
            'title': ticket.title,
            'comment': _('Accepted resolution and closed ticket'),
            }

        return update_ticket(request, ticket_id)

    return render_to_response('helpdesk/ticket.html',
        RequestContext(request, {
            'ticket': ticket,
            'active_users': User.objects.filter(is_active=True).filter(is_staff=True),
            'priorities': Ticket.PRIORITY_CHOICES,
            'preset_replies': PreSetReply.objects.filter(Q(queues=ticket.queue) | Q(queues__isnull=True)),
            'tags_enabled': HAS_TAG_SUPPORT
        }))
view_ticket = staff_member_required(view_ticket)

@systemuser_required
@render_to('helpdesk/followup_edit.html')
def followup_edit(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 
        
        if id:
            model = FollowUp.objects.get(id=id)

                
            form = FollowUpForm(request.POST, instance=model) 
            if  not (request.user.account.has_perm('helpdesk.change_followup')):
                messages.error(request, _(u'У вас нет прав на редактирование комментариев к заявке'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)
        else:
            form = FollowUpForm(request.POST, request.FILES) 
            if  not (request.user.account.has_perm('helpdesk.add_followup')):
                messages.error(request, _(u'У вас нет прав на добавление комментариев к заявке'), extra_tags='alert-danger')
                return HttpResponseRedirect(request.path)



        if form.is_valid():
            model = form.save(commit=False)
            model.save()
            followup_type = form.cleaned_data.get('followup_type')
            if followup_type=='comment':
                if not id:
                    model.title = _(u'Добавлен комментарий от %(USER)s ') % {'USER': request.user.account}
            elif followup_type=='files':
                if not id:
                    model.title = _(u'Добавлен файл от %(USER)s ') % {'USER': request.user.account}
                    
                files = []
                if request.FILES:
                    import mimetypes, os
                    for file in request.FILES.getlist('file'):
                        filename = file.name.replace(' ', '_')
                        a = Attachment(
                            followup=model,
                            filename=filename,
                            mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                            size=file.size,
                            )
                        a.file.save(file.name, file, save=False)
                        a.save()
            
                        if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                            # Only files smaller than 512kb (or as defined in
                            # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                            files.append(a.file.path)

            elif followup_type=='new_status':
                model.title = _(u'Статус заявки изменён %(USER)s ') % {'USER': request.user.account}
                if model.new_status!=model.ticket:
                    model.ticket.status = model.new_status
                    if model.new_status in [3,4]:
                        model.ticket.resolution = model.comment
                    model.ticket.save()
                    log('EDIT', request.user, model.ticket)
            model.systemuser = request.user.account


            model.save()

            from django.template import loader, Context


            
            
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Комментарий успешно сохранён.'), extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, _(u'При сохранении комментария возникли ошибки.'), extra_tags='alert-danger')
            if form._errors:
                for k, v in form._errors.items():
                    messages.error(request, '%s=>%s' % (k, ','.join(v)), extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        id = request.GET.get("id")
        ticket_id = request.GET.get("ticket_id")
        followup_type = request.GET.get("followup_type") or 'comment'
        new_status = request.GET.get("new_status")

        if  not (request.user.account.has_perm('helpdesk.add_followup')):
            messages.error(request, _(u'У вас нет прав на создание комментариев.'), extra_tags='alert-danger')
            return {}
        if id:

            item = FollowUp.objects.get(id=id)
            
            form = FollowUpForm(instance=item)
        else:
            if new_status:
                form = FollowUpForm(initial={'ticket': Ticket.objects.get(id=ticket_id), 'followup_type': followup_type, 'new_status':2})
            else:
                form = FollowUpForm(initial={'ticket': Ticket.objects.get(id=ticket_id), 'followup_type': followup_type})

    return { 'form':form, 'status': False} 

@systemuser_required
@render_to('helpdesk/ticket_assign.html')
def ticket_assign(request):
    id = request.POST.get("id")

    item = None

    if request.method == 'POST': 
        

        form = AssignToForm(request.POST, request.FILES) 
        if  not (request.user.account.has_perm('helpdesk.ticket_reassign')):
            messages.error(request, _(u'У вас нет прав на перевод заявок'), extra_tags='alert-danger')
            return HttpResponseRedirect(request.path)



        if form.is_valid():
            ticket = form.cleaned_data['ticket']
            model = ticket
            model.assigned_to = form.cleaned_data['systemuser']

            model.save(force_update=True)
            
            print model.assigned_to
 


            
            
            log('EDIT', request.user, model) if id else log('CREATE', request.user, model) 
            messages.success(request, _(u'Задача переведена.'), extra_tags='alert-success')
            return {'form':form,  'status': True} 
        else:
            messages.error(request, _(u'При переводе заявки возникли ошибки.'), extra_tags='alert-danger')
            if form._errors:
                for k, v in form._errors.items():
                    messages.error(request, '%s=>%s' % (k, ','.join(v)), extra_tags='alert-danger')
            return {'form':form,  'status': False} 
    else:
        ticket_id = request.GET.get("ticket_id")
        systemuser_id = request.GET.get("systemuser_id")

        if  not (request.user.account.has_perm('helpdesk.ticket_reassign')):
            messages.error(request, _(u'У вас нет прав на перевод заявок.'), extra_tags='alert-danger')
            return {}
        if ticket_id:

            item = Ticket.objects.get(id=ticket_id)
            
            if systemuser_id and item:
                #BUG. User can assign to anyone
                item.assigned_to = request.user.account
                item.save()
                return {'form':None,  'status': True} 
            form = AssignToForm(initial={'ticket': item, })

    return { 'form':form, 'status': False} 

def update_ticket(request, ticket_id, public=False):
    if not (public or (request.user.is_authenticated() and request.user.is_active and request.user.is_staff)):
        return HttpResponseForbidden(_('Sorry, you need to login to do that.'))

    ticket = get_object_or_404(Ticket, id=ticket_id)


    comment = request.POST.get('comment', '')
    new_status = int(request.POST.get('new_status', ticket.status))
    title = request.POST.get('title', ticket.title)
    public = request.POST.get('public', public)
       
    owner = int(request.POST.get('owner', 0))
    priority = int(request.POST.get('priority', ticket.priority))
    tags = request.POST.get('tags', '')
    
    if public:
        ticket.notify_owner=True
    else:
        ticket.notify_owner=False
    # We need to allow the 'ticket' and 'queue' contexts to be applied to the
    # comment.
    from django.template import loader, Context
    context = safe_template_context(ticket)
    comment = loader.get_template_from_string(comment).render(Context(context))

    if owner is None and ticket.assigned_to:
        owner = ticket.assigned_to.id

    f = FollowUp(ticket=ticket, date=datetime.now(), comment=comment)

    if request.user.is_authenticated():
        f.user = request.user

    f.public = public

    reassigned = False

    if owner is not None:
        if owner != 0 and ((ticket.assigned_to and owner != ticket.assigned_to.id) or not ticket.assigned_to):
            new_user = User.objects.get(id=owner)
            f.title = _('Assigned to %(username)s') % {
                'username': new_user.username,
                }
            ticket.assigned_to = new_user
            reassigned = True
        elif owner == 0 and ticket.assigned_to is not None:
            f.title = _('Unassigned')
            ticket.assigned_to = None

    if new_status != ticket.status:
        ticket.status = new_status
        ticket.save()
        f.new_status = new_status
        if f.title:
            f.title += ' and %s' % ticket.get_status_display()
        else:
            f.title = '%s' % ticket.get_status_display()

    if not f.title:
        if f.comment:
            f.title = _('Comment')
        else:
            f.title = _('Updated')

    f.save()
    files = []
    if request.FILES:
        import mimetypes, os
        for file in request.FILES.getlist('attachment'):
            filename = file.name.replace(' ', '_')
            a = Attachment(
                followup=f,
                filename=filename,
                mime_type=mimetypes.guess_type(filename)[0] or 'application/octet-stream',
                size=file.size,
                )
            a.file.save(file.name, file, save=False)
            a.save()

            if file.size < getattr(settings, 'MAX_EMAIL_ATTACHMENT_SIZE', 512000):
                # Only files smaller than 512kb (or as defined in
                # settings.MAX_EMAIL_ATTACHMENT_SIZE) are sent via email.
                files.append(a.file.path)


    if title != ticket.title:
        c = TicketChange(
            followup=f,
            field=_('Title'),
            old_value=ticket.title,
            new_value=title,
            )
        c.save()
        ticket.title = title

    if priority != ticket.priority:
        c = TicketChange(
            followup=f,
            field=_('Priority'),
            old_value=ticket.priority,
            new_value=priority,
            )
        c.save()
        ticket.priority = priority

    if HAS_TAG_SUPPORT:
        if tags != ticket.tags:
            c = TicketChange(
                followup=f,
                field=_('Tags'),
                old_value=ticket.tags,
                new_value=tags,
                )
            c.save()
            ticket.tags = tags

    if f.new_status == Ticket.RESOLVED_STATUS:
        ticket.resolution = comment

    messages_sent_to = []

    context.update(
        resolution=ticket.resolution,
        comment=f.comment,
        )

    if ticket.submitter_email and public and (f.comment or (f.new_status in (Ticket.RESOLVED_STATUS, Ticket.CLOSED_STATUS))):

        if f.new_status == Ticket.RESOLVED_STATUS:
            template = 'resolved_owner'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template = 'closed_owner'
        else:
            template = 'updated_owner'

        send_templated_mail(
            template,
            context,
            recipients=ticket.submitter_email,
            sender=ticket.queue.from_address,
            fail_silently=True,
            files=files,
            )
        messages_sent_to.append(ticket.submitter_email)

        for cc in ticket.ticketcc_set.all():
            if cc.email_address not in messages_sent_to:
                send_templated_mail(
                    template,
                    context,
                    recipients=cc.email_address,
                    sender=ticket.queue.from_address,
                    fail_silently=True,
                    )
                messages_sent_to.append(cc.email_address)

    if ticket.assigned_to and request.user.account != ticket.assigned_to and ticket.assigned_to.email and ticket.assigned_to.email not in messages_sent_to:
        # We only send e-mails to staff members if the ticket is updated by
        # another user. The actual template varies, depending on what has been
        # changed.
        if reassigned:
            template_staff = 'assigned_to'
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_staff = 'resolved_asigned_to'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template_staff = 'closed_assigned_to'
        else:
            template_staff = 'updated_assigned_to'

        if (not reassigned or ( reassigned and ticket.assigned_to.usersettings.settings.get('email_on_ticket_assign', False))) or (not reassigned and ticket.assigned_to.usersettings.settings.get('email_on_ticket_change', False)):
            send_templated_mail(
                template_staff,
                context,
                recipients=ticket.assigned_to.email,
                sender=ticket.queue.from_address,
                fail_silently=True,
                files=files,
                )
            messages_sent_to.append(ticket.assigned_to.email)

    if ticket.queue.updated_ticket_cc and ticket.queue.updated_ticket_cc not in messages_sent_to:
        if reassigned:
            template_cc = 'assigned_cc'
        elif f.new_status == Ticket.RESOLVED_STATUS:
            template_cc = 'resolved_cc'
        elif f.new_status == Ticket.CLOSED_STATUS:
            template_cc = 'closed_cc'
        else:
            template_cc = 'updated_cc'

        send_templated_mail(
            template_cc,
            context,
            recipients=ticket.queue.updated_ticket_cc,
            sender=ticket.queue.from_address,
            fail_silently=True,
            files=files,
            )

    ticket.save()

    if request.user.is_staff:
        return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        return HttpResponseRedirect(ticket.ticket_url)


def mass_update(request):
    tickets = request.POST.getlist('ticket_id')
    action = request.POST.get('action', None)
    if not (tickets and action):
        return HttpResponseRedirect(reverse('helpdesk_list'))

    if action.startswith('assign_'):
        parts = action.split('_')
        user = User.objects.get(id=parts[1])
        action = 'assign'
    elif action == 'take':
        user = request.user
        action = 'assign'

    for t in Ticket.objects.filter(id__in=tickets):
        if action == 'assign' and t.assigned_to != user:
            t.assigned_to = user
            t.save()
            f = FollowUp(ticket=t, date=datetime.now(), title=_('Assigned to %(username)s in bulk update' % {'username': user.username}), public=True, user=request.user)
            f.save()
        elif action == 'unassign' and t.assigned_to is not None:
            t.assigned_to = None
            t.save()
            f = FollowUp(ticket=t, date=datetime.now(), title=_('Unassigned in bulk update'), public=True, user=request.user)
            f.save()
        elif action == 'close' and t.status != Ticket.CLOSED_STATUS:
            t.status = Ticket.CLOSED_STATUS
            t.save()
            f = FollowUp(ticket=t, date=datetime.now(), title=_('Closed in bulk update'), public=False, user=request.user, new_status=Ticket.CLOSED_STATUS)
            f.save()
        elif action == 'close_public' and t.status != Ticket.CLOSED_STATUS:
            t.status = Ticket.CLOSED_STATUS
            t.save()
            f = FollowUp(ticket=t, date=datetime.now(), title=_('Closed in bulk update'), public=True, user=request.user, new_status=Ticket.CLOSED_STATUS)
            f.save()
            # Send email to Submitter, Owner, Queue CC
            context = {
                'ticket': t,
                'queue': t.queue,
                'resolution': t.resolution,
            }

            messages_sent_to = []

            if t.submitter_email:
                send_templated_mail(
                    'closed_owner',
                    context,
                    recipients=t.submitter_email,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )
                messages_sent_to.append(t.submitter_email)

            for cc in ticket.ticketcc_set.all():
                if cc.email_address not in messages_sent_to:
                    send_templated_mail(
                        'closed_owner',
                        context,
                        recipients=cc.email_address,
                        sender=ticket.queue.from_address,
                        fail_silently=True,
                        )
                    messages_sent_to.append(cc.email_address)

            if t.assigned_to and request.user != t.assigned_to and t.assigned_to.email and t.assigned_to.email not in messages_sent_to:
                send_templated_mail(
                    'closed_assigned_to',
                    context,
                    recipients=t.assigned_to.email,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )
                messages_sent_to.append(t.assigned_to.email)

            if t.queue.updated_ticket_cc and t.queue.updated_ticket_cc not in messages_sent_to:
                send_templated_mail(
                    'closed_cc',
                    context,
                    recipients=t.queue.updated_ticket_cc,
                    sender=t.queue.from_address,
                    fail_silently=True,
                    )

        elif action == 'delete':
            t.delete()

    return HttpResponseRedirect(reverse('helpdesk_list'))
mass_update = staff_member_required(mass_update)

def ticket_list(request):
    context = {}

    # Query_params will hold a dictionary of paramaters relating to
    # a query, to be saved if needed:
    query_params = {
        'filtering': {},
        'sorting': None,
        'sortreverse': False,
        'keyword': None,
        'other_filter': None,
        }

    from_saved_query = False

    # If the user is coming from the header/navigation search box, lets' first
    # look at their query to see if they have entered a valid ticket number. If
    # they have, just redirect to that ticket number. Otherwise, we treat it as
    # a keyword search.

    if request.GET.get('search_type', None) == 'header':
        query = request.GET.get('q')
        filter = None
        if query.find('-') > 0:
            queue, id = query.split('-')
            try:
                id = int(id)
            except ValueError:
                id = None

            if id:
                filter = {'queue__slug': queue, 'id': id }
        else:
            try:
                query = int(query)
            except ValueError:
                query = None

            if query:
                filter = {'id': int(query) }

        if filter:
            try:
                ticket = Ticket.objects.get(**filter)
                return HttpResponseRedirect(ticket.staff_url)
            except Ticket.DoesNotExist:
                # Go on to standard keyword searching
                pass

    if request.GET.get('saved_query', None):
        from_saved_query = True
        try:
            saved_query = SavedSearch.objects.get(pk=request.GET.get('saved_query'))
        except SavedSearch.DoesNotExist:
            return HttpResponseRedirect(reverse('helpdesk_list'))
        if not (saved_query.shared or saved_query.user == request.user):
            return HttpResponseRedirect(reverse('helpdesk_list'))

        import cPickle
        from helpdesk.lib import b64decode
        query_params = cPickle.loads(b64decode(str(saved_query.query)))
    elif not (  request.GET.has_key('queue')
            or  request.GET.has_key('assigned_to')
            or  request.GET.has_key('owner')
            or  request.GET.has_key('status')
            or  request.GET.has_key('q')
            or  request.GET.has_key('sort')
            or  request.GET.has_key('sortreverse') 
            or  request.GET.has_key('tags') ):

        # Fall-back if no querying is being done, force the list to only
        # show open/reopened/resolved (not closed) cases sorted by creation
        # date.

        query_params = {
            'filtering': {'status__in': [1, 2, 3]},
            'sorting': 'created',
        }
    else:
        queues = request.GET.getlist('queue')
        if queues:
            queues = [int(q) for q in queues]
            query_params['filtering']['queue__id__in'] = queues

        assigned_to = request.GET.getlist('assigned_to')
        if assigned_to:
            assigned_to = [int(u) for u in assigned_to]
            query_params['filtering']['assigned_to__id__in'] = assigned_to

        owner = request.GET.getlist('owner')
        if owner:
            owner = [int(u) for u in owner]
            query_params['filtering']['owner__id__in'] = owner
            
        statuses = request.GET.getlist('status')
        if statuses:
            statuses = [int(s) for s in statuses]
            query_params['filtering']['status__in'] = statuses

        ### KEYWORD SEARCHING
        q = request.GET.get('q', None)

        if q:
            qset = (
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(resolution__icontains=q) |
                Q(submitter_email__icontains=q)
            )
            context = dict(context, query=q)

            query_params['other_filter'] = qset

        ### SORTING
        sort = request.GET.get('sort', None)
        if sort not in ('status', 'assigned_to', 'created', 'title', 'queue', 'priority'):
            sort = 'created'
        query_params['sorting'] = sort

        sortreverse = request.GET.get('sortreverse', None)
        query_params['sortreverse'] = sortreverse

    ticket_qs = apply_query(Ticket.objects.select_related(), query_params)

    ## TAG MATCHING
    if HAS_TAG_SUPPORT:
        tags = request.GET.getlist('tags')
        if tags:
            ticket_qs = TaggedItem.objects.get_by_model(ticket_qs, tags)
            query_params['tags'] = tags

    ticket_paginator = paginator.Paginator(ticket_qs, request.user.usersettings.settings.get('tickets_per_page') or 20)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
         page = 1

    try:
        tickets = ticket_paginator.page(page)
    except (paginator.EmptyPage, paginator.InvalidPage):
        tickets = ticket_paginator.page(ticket_paginator.num_pages)

    search_message = ''
    if context.has_key('query') and settings.DATABASE_ENGINE.startswith('sqlite'):
        search_message = _('<p><strong>Note:</strong> Your keyword search is case sensitive because of your database. This means the search will <strong>not</strong> be accurate. By switching to a different database system you will gain better searching! For more information, read the <a href="http://docs.djangoproject.com/en/dev/ref/databases/#sqlite-string-matching">Django Documentation on string matching in SQLite</a>.')


    import cPickle
    from helpdesk.lib import b64encode
    urlsafe_query = b64encode(cPickle.dumps(query_params))

    user_saved_queries = SavedSearch.objects.filter(Q(user=request.user) | Q(shared__exact=True))

    query_string = []
    for get_key, get_value in request.GET.iteritems():
        if get_key != "page":
            query_string.append("%s=%s" % (get_key, get_value))

    tag_choices = [] 
    if HAS_TAG_SUPPORT:
        # FIXME: restrict this to tags that are actually in use
        tag_choices = Tag.objects.all()

    return render_to_response('helpdesk/ticket_list.html',
        RequestContext(request, dict(
            context,
            query_string="&".join(query_string),
            tickets=tickets,
            assigned_to_choices=User.objects.filter(is_active=True, is_staff=True),
            owner_choices=User.objects.filter(is_active=True),
            queue_choices=Queue.objects.all(),
            status_choices=Ticket.STATUS_CHOICES,
            tag_choices=tag_choices,
            urlsafe_query=urlsafe_query,
            user_saved_queries=user_saved_queries,
            query_params=query_params,
            from_saved_query=from_saved_query,
            search_message=search_message,
            tags_enabled=HAS_TAG_SUPPORT
        )))
ticket_list = staff_member_required(ticket_list)

@staff_member_required
def tickets(request):
    
    if request.method == 'GET':
        
        
        items = Ticket.objects.all()
        if request.GET:
            form = FilterForm(request.GET)
            form.fields['saved_query'].queryset = SavedSearch.objects.filter(Q(shared=True)|Q(systemuser=request.user.account))
            filter = {}
            save = request.GET.get('save')
            run = request.GET.get('run')
            if form.is_valid():
                saved_query = form.cleaned_data.get('saved_query')
                
                if run:
                    print saved_query.query
                    print pickle.loads(saved_query.query)
                    data = pickle.loads(saved_query.query) # load and check query
                    print data
                    form = FilterForm(data)
                    form.is_valid()
                    
                date_start =  form.cleaned_data.get('date_start')
                if date_start:
                    filter.update({'created__gte': date_start})
                    
                date_end =  form.cleaned_data.get('date_end')
                if date_end:
                    filter.update({'created__lte': date_end})
                    
                owner =  form.cleaned_data.get('owner')
                if owner:
                    filter.update({'owner': owner})
                    
                queue =  form.cleaned_data.get('queue')
                if queue:
                    filter.update({'queue__in': queue})

                account =  form.cleaned_data.get('account')
                if account:
                    filter.update({'account': account})

                assigned_to =  form.cleaned_data.get('assigned_to')
                if assigned_to:
                    filter.update({'assigned_to__in': assigned_to})
                    
                assigned_to =  form.cleaned_data.get('assigned_to')
                if assigned_to:
                    filter.update({'assigned_to': assigned_to})
                    
                status =  form.cleaned_data.get('status')
                
                if status and str(status)!='0':
                    filter.update({'status__in': status})
                
                
                priority =  form.cleaned_data.get('priority')
                
                if priority and str(priority)!='0':
                    filter.update({'priority': priority})

                keywords =  form.cleaned_data.get('keywords')
                
                if keywords:
                    filter.update({'title__icontains': keywords})
                    filter.update({'description__icontains': keywords})

                    #print saved_query.query
                    

                
                #===============================================================
                # tags =  form.cleaned_data.get('tags')
                # 
                # if tags:
                #    filter.update({'tags__in': ', '.join([tag.name for tag in tags])})
                #===============================================================
                print '!!!!!!!!!', save
                if save:
                    print '!!!!!!!!!', filter
                    filter_name =  form.cleaned_data.get('filter_name')
                    m = SavedSearch.objects.create(title=filter_name, query=pickle.dumps(request.GET), systemuser=request.user.account, shared=form.cleaned_data.get('share_filter'))
                    m.save()
                    

                items = items.filter(**filter)
        else:
            form = FilterForm()
            form.fields['saved_query'].queryset = SavedSearch.objects.filter(Q(shared=True)|Q(systemuser=request.user.account))
        
        table = TicketTable(items)
        table_to_report = RequestConfig(request, paginate=False if request.GET.get('paginate')=='False' else {"per_page": request.COOKIES.get("ebs_per_page")}).configure(table)
        if table_to_report:
            return create_report_http_response(table_to_report, request)

        
    return render_to_response('helpdesk/tickets.html',
        RequestContext(request, {
            'form': form,
            'table': table
        }))
        

def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = EditTicketForm(request.POST, instance=ticket)
        if form.is_valid():
            ticket = form.save()
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        form = EditTicketForm(instance=ticket)
    
    return render_to_response('helpdesk/create_ticket.html',
        RequestContext(request, {
            'form': form,
            'tags_enabled': HAS_TAG_SUPPORT,
        }))
edit_ticket = staff_member_required(edit_ticket)

def create_ticket(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if id:
            ticket = get_object_or_404(Ticket, id=id)
            form = EditTicketForm(request.POST, request.FILES, instance=ticket)
        else:
            form = TicketForm(request.POST, request.FILES)

        
        
        if form.is_valid():
            if id:
                ticket = form.save()
            else:
                ticket = form.save(user=request.user)
            return HttpResponseRedirect(ticket.get_absolute_url())
    else:
        initial_data = {}
        id = request.GET.get('id')
        account_id = request.GET.get('account_id')
        if account_id:
            initial_data['account'] = Account.objects.get(id=account_id)
        
        
        if request.user.usersettings.settings.get('use_email_as_submitter', False) and request.user.account.email:
            initial_data['submitter_email'] = request.user.account.email
            
        if id:
            ticket = get_object_or_404(Ticket, id=id)
            form = EditTicketForm(instance=ticket)
        else:
            form = TicketForm(initial=initial_data)
        
  
        form.fields['assigned_to'].initial = request.user.account
        form.fields['owner'].initial = request.user
    
        
    return render_to_response('helpdesk/create_ticket.html',
        RequestContext(request, {
            'form': form,
            'tags_enabled': HAS_TAG_SUPPORT,
        }))
create_ticket = staff_member_required(create_ticket)


def raw_details(request, type):
    # TODO: This currently only supports spewing out 'PreSetReply' objects,
    # in the future it needs to be expanded to include other items. All it
    # does is return a plain-text representation of an object.

    if not type in ('preset',):
        raise Http404

    if type == 'preset' and request.GET.get('id', False):
        try:
            preset = PreSetReply.objects.get(id=request.GET.get('id'))
            return HttpResponse(preset.body)
        except PreSetReply.DoesNotExist:
            raise Http404

    raise Http404
raw_details = staff_member_required(raw_details)


def hold_ticket(request, ticket_id, unhold=False):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if unhold:
        ticket.on_hold = False
        title = _('Ticket taken off hold')
    else:
        ticket.on_hold = True
        title = _('Ticket placed on hold')

    f = FollowUp(
        ticket = ticket,
        systemuser = request.user.account,
        title = title,
        date = datetime.now(),
        public = True,
    )
    f.save()

    ticket.save()

    return HttpResponseRedirect(ticket.get_absolute_url())
hold_ticket = staff_member_required(hold_ticket)


def unhold_ticket(request, ticket_id):
    return hold_ticket(request, ticket_id, unhold=True)
unhold_ticket = staff_member_required(unhold_ticket)


def rss_list(request):
    return render_to_response('helpdesk/rss_list.html',
        RequestContext(request, {
            'queues': Queue.objects.all(),
        }))
rss_list = staff_member_required(rss_list)


def report_index(request):
    number_tickets = Ticket.objects.all().count()
    return render_to_response('helpdesk/report_index.html',
        RequestContext(request, {
            'number_tickets': number_tickets,
        }))
report_index = staff_member_required(report_index)


def run_report(request, report):
    priority_sql = []
    priority_columns = []
    for p in Ticket.PRIORITY_CHOICES:
        print dir(p[1])
        priority_sql.append("COUNT(CASE t.priority WHEN '%s' THEN t.id END) AS \"%s\"" % (p[0], p[1]._proxy____cast()))
        priority_columns.append("%s" % p[1]._proxy____cast())
    priority_sql = ", ".join(priority_sql)

    status_sql = []
    status_columns = []
    for s in Ticket.STATUS_CHOICES:
        status_sql.append("COUNT(CASE t.status WHEN '%s' THEN t.id END) AS \"%s\"" % (s[0], s[1]._proxy____cast()))
        status_columns.append("%s" % s[1]._proxy____cast())
    status_sql = ", ".join(status_sql)

    queue_sql = []
    queue_columns = []
    for q in Queue.objects.all():
        queue_sql.append("COUNT(CASE t.queue_id WHEN '%s' THEN t.id END) AS \"%s\"" % (q.id, q.title))
        queue_columns.append(q.title)
    queue_sql = ", ".join(queue_sql)

    month_sql = []
    months = (
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
    )
    month_columns = []

    first_ticket = Ticket.objects.all().order_by('created')[0]
    first_month = first_ticket.created.month
    first_year = first_ticket.created.year

    last_ticket = Ticket.objects.all().order_by('-created')[0]
    last_month = last_ticket.created.month
    last_year = last_ticket.created.year

    periods = []
    year, month = first_year, first_month
    working = True

    while working:
        temp = (year, month)
        month += 1
        if month > 12:
            year += 1
            month = 1
        if (year > last_year) or (month > last_month and year >= last_year):
            working = False
        periods.append((temp, (year, month)))

    for (low_bound, upper_bound) in periods:
        low_sqlmonth = '%s-%02i-01' % (low_bound[0], low_bound[1])
        upper_sqlmonth = '%s-%02i-01' % (upper_bound[0], upper_bound[1])
        desc = '%s %s' % (months[low_bound[1]-1], low_bound[0])
        month_sql.append("""
          COUNT(
             CASE 1 = 1
             WHEN (date(t.created) >= date('%s')
                  AND date(t.created) < date('%s')) THEN t.id END) AS "%s"
             """ % (low_sqlmonth, upper_sqlmonth, desc))
        month_columns.append(desc)

    month_sql = ", ".join(month_sql)

    queue_base_sql = """
            SELECT      q.title as queue, %s
                FROM    helpdesk_ticket t,
                        helpdesk_queue q
                WHERE   q.id =  t.queue_id
                GROUP BY queue
                ORDER BY queue;
                """

    user_base_sql = """
            SELECT      u.username as username, %s
                FROM    helpdesk_ticket t,
                        auth_user u
                WHERE   u.id =  t.assigned_to_id
                GROUP BY u.username
                ORDER BY u.username;
                """

    if report == 'userpriority':
        sql = user_base_sql % priority_sql
        columns = ['username'] + priority_columns
        title = _(u'User by priority')

    elif report == 'userqueue':
        sql = user_base_sql % queue_sql
        columns = ['username'] + queue_columns
        title = _(u'User by queue')

    elif report == 'userstatus':
        sql = user_base_sql % status_sql
        columns = ['username'] + status_columns
        title = _(u'User by status')

    elif report == 'usermonth':
        sql = user_base_sql % month_sql
        columns = ['username'] + month_columns
        title = _(u'User by month')

    elif report == 'queuepriority':
        sql = queue_base_sql % priority_sql
        columns = ['queue'] + priority_columns
        title = _(u'Queue by priority')

    elif report == 'queuestatus':
        sql = queue_base_sql % status_sql
        columns = ['queue'] + status_columns
        title = _(u'Queue by status')

    elif report == 'queuemonth':
        sql = queue_base_sql % month_sql
        columns = ['queue'] + month_columns
        title = _(u'Queue by month')


    cursor = connection.cursor()
    cursor.execute(sql)
    report_output = query_to_dict(cursor.fetchall(), cursor.description)

    data = []

    for record in report_output:
        line = []
        for c in columns:
            c = c.encode('utf-8')
            line.append(record[c])
        data.append(line)

    if report in ('queuemonth', 'usermonth'):
        chart_url = line_chart([columns] + data)
    elif report in ('queuestatus', 'queuepriority', 'userstatus', 'userpriority'):
        chart_url = bar_chart([columns] + data)
    else:
        chart_url = ''

    return render_to_response('helpdesk/report_output.html',
        RequestContext(request, {
            'headings': columns,
            'data': data,
            'chart': chart_url,
            'title': title,
        }))
run_report = staff_member_required(run_report)


def save_query(request):
    title = request.POST.get('title', None)
    shared = request.POST.get('shared', False)
    query_encoded = request.POST.get('query_encoded', None)

    if not title or not query_encoded:
        return HttpResponseRedirect(reverse('helpdesk_list'))

    query = SavedSearch(title=title, shared=shared, query=query_encoded, user=request.user)
    query.save()

    return HttpResponseRedirect('%s?saved_query=%s' % (reverse('helpdesk_list'), query.id))
save_query = staff_member_required(save_query)


def delete_saved_query(request, id):
    query = get_object_or_404(SavedSearch, id=id, user=request.user)

    if request.method == 'POST':
        query.delete()
        return HttpResponseRedirect(reverse('helpdesk_list'))
    else:
        return render_to_response('helpdesk/confirm_delete_saved_query.html',
            RequestContext(request, {
                'query': query,
                }))
delete_saved_query = staff_member_required(delete_saved_query)


def user_settings(request):
    s = request.user.usersettings
    if request.POST:
        form = UserSettingsForm(request.POST)
        if form.is_valid():
            s.settings = form.cleaned_data
            s.save()
    else:
        form = UserSettingsForm(s.settings)

    return render_to_response('helpdesk/user_settings.html',
        RequestContext(request, {
            'form': form,
        }))
user_settings = staff_member_required(user_settings)


def email_ignore(request):
    return render_to_response('helpdesk/email_ignore_list.html',
        RequestContext(request, {
            'ignore_list': IgnoreEmail.objects.all(),
        }))
email_ignore = superuser_required(email_ignore)


def email_ignore_add(request):
    if request.method == 'POST':
        form = EmailIgnoreForm(request.POST)
        if form.is_valid():
            ignore = form.save()
            return HttpResponseRedirect(reverse('helpdesk_email_ignore'))
    else:
        form = EmailIgnoreForm(request.GET)

    return render_to_response('helpdesk/email_ignore_add.html',
        RequestContext(request, {
            'form': form,
        }))
email_ignore_add = superuser_required(email_ignore_add)


def email_ignore_del(request, id):
    ignore = get_object_or_404(IgnoreEmail, id=id)
    if request.method == 'POST':
        ignore.delete()
        return HttpResponseRedirect(reverse('helpdesk_email_ignore'))
    else:
        return render_to_response('helpdesk/email_ignore_del.html',
            RequestContext(request, {
                'ignore': ignore,
            }))
email_ignore_del = superuser_required(email_ignore_del)

def ticket_cc(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    copies_to = ticket.ticketcc_set.all()
    return render_to_response('helpdesk/ticket_cc_list.html',
        RequestContext(request, {
            'copies_to': copies_to,
            'ticket': ticket,
        }))
ticket_cc = staff_member_required(ticket_cc)

def ticket_cc_add(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if request.method == 'POST':
        form = TicketCCForm(request.POST)
        if form.is_valid():
            ticketcc = form.save(commit=False)
            ticketcc.ticket = ticket
            ticketcc.save()
            return HttpResponseRedirect(reverse('helpdesk_ticket_cc', kwargs={'ticket_id': ticket.id}))
    else:
        form = TicketCCForm()
    return render_to_response('helpdesk/ticket_cc_add.html',
        RequestContext(request, {
            'ticket': ticket,
            'form': form,
        }))
ticket_cc_add = staff_member_required(ticket_cc_add)

def ticket_cc_del(request, ticket_id, cc_id):
    cc = get_object_or_404(TicketCC, ticket__id=ticket_id, id=cc_id)
    if request.method == 'POST':
        cc.delete()
        return HttpResponseRedirect(reverse('helpdesk_ticket_cc', kwargs={'ticket_id': cc.ticket.id}))
    return render_to_response('helpdesk/ticket_cc_del.html',
        RequestContext(request, {
            'cc': cc,
        }))
ticket_cc_del = staff_member_required(ticket_cc_del)


@systemuser_required
@render_to('helpdesk/queueselect_window.html')
def queueselect(request):

    form = TicketTypeForm()
    
    return { 'form':form} 

@systemuser_required
@ajax_request
def ticket_info(request):

    ticket = Ticket.objects.get(id=request.GET.get('id'))
    
    return { 'body': ticket.description} 
