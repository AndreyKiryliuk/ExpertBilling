Ext.onReady(function(){
    Ext.ns('EBS.forms.ebs_accountsPanel')
    EBS.conponents.accountsGrid = Ext.extend(EBS.base.GridPanel, {
         initComponent: function() {
                /*
                 *ф-я вызывается в менюшке. В качестве параметров идут self, вызываемая ф-я, если нужно - параметры.
                 *берем функцию через  eval и вызываем ее с параметрами
                 *id у self обязательна.
                 *
                 *Будут перенесены в базовый компонент. менять сразу во всех компонентах!
                 **/
                this.tbFormCallBack = function(self, action){EBS.displayForm(self.xtype, action, self)}
                this.tbCustomFormCallBack = function(self, action){EBS.displayCustomForm(self.xtype, action, self)}
                
                this.tbFormInTabCallBack = function(self, action, id){
                	//alert(id);
                	//alert(self.selModel);
                	
                		id=self.selModel.selections.items[0].id;
                		//alert(self.selModel.selections.items[0]);
                	
                	EBS.displayFormInTab(self.xtype, action,id, self)
                	}
                this.tbWindowCallBack = function(self, action){EBS.displayWindow(self.xtype, action, self)}
                this.tbCommandCallBack = function(self, a,b,c){
                    eval(action)(a,b,c)
                }

             // MENU
             this.topToolbar = new Ext.Toolbar({
                    enableOverflow: true,
                    items:[
                         {
                            icon: media+'icons/16/pencil.png',
                            height:16,width:16,
                            text: i18n.edit,
                            handler: this.tbFormInTabCallBack.createCallback(this, 'edit_user',null)
                        },{
                            text: i18n.print,
                            icon: media+'icons/16/printer.png',
                            height:16,width:16,
                            tooltip: i18n.printToolTip,
                            handler: function(){Ext.ux.Printer.print(Ext.getCmp('accounts_list'))}
                        },
                        {xtype: 'tbseparator'},
                        {
                            xtype: 'tbbutton',
                            text: 'Действия',
                            icon: media+'icons/16/new/user.png',
                            height:16,width:16,
                            menu: [
                                {
                                    text : "Редактировать кредит",
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbCustomFormCallBack.createCallback(this,'edit_credit')
                                },{
                                    text : i18n.accounts.edit_server,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'edit_server')
                                },{
                                    text : i18n.accounts.set_ipn,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_ipn')
                                },{
                                    text : i18n.accounts.set_vpn,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'edit_server')
                                },{
                                    text : i18n.accounts.set_mac,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_mac')
                                },{
                                    text : i18n.accounts.set_ipn_from_pool,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_ipn_from_pool')
                                },{
                                    text : i18n.accounts.set_vpn_from_pool,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_vpn_from_pool')
                                },{
                                    text : i18n.accounts.set_flags,
                                    icon: media+'icons/16/new/cog.png',
                                    handler: this.tbFormCallBack.createCallback(this,'set_flags')
                                }

                            ]
                        },{xtype: 'tbseparator'},{
                            text: i18n.save,
                            icon: media+'icons/16/accept.png',
                            height:16,width:16,
                            tooltip: i18n.saveToolTip,
                            handler: EBS.store.accounts.save
                        }

                    ]
                });






             Ext.apply(this, {
                                id:'accounts_list',
                                store   : EBS.store.accounts,
                                closable:true,
                              //  plugins : [this.filters],
                                tbar    : this.topToolbar,
                                columns : [
                                    {
                                        header   : '#',
                                        sortable : true,
                                        //width    : 85,
                                        locked: true,
                                        dataIndex: id,
                                        filter: {
                                            type: 'numeric'
                                        }

                                    },                                
                                    {
                                        header   : i18n.accounts.username,
                                        sortable : true,
                                        width    : 85,
                                        locked: true,
                                        dataIndex: 'username',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : i18n.accounts.fio,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'fullname',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                    {
                                        header   : i18n.accounts.ballance,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'ballance',
                                        renderer: EBS.moneyRenderer,
                                        filter: {
                                            type: 'string'
                                        }

                                    },     
                                    {
                                        header   : i18n.accounts.nas,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'nas',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                   {
                                        header   : i18n.accounts.credit,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'credit',
                                        renderer: EBS.moneyRenderer,
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                   {
                                        header   : i18n.accounts.vpn_ip_address,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'vpn_ip_address',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                   {
                                        header   : i18n.accounts.ipn_ip_address,
                                        sortable : true,
                                        //autoexpand:true,
                                        width:200,
                                        dataIndex: 'ipn_ip_address',
                                        filter: {
                                            type: 'string'
                                        }

                                    },                                    {
                                        header   : i18n.accounts.created,
                                        width    : 115,
                                        sortable : true,
                                        renderer : Ext.util.Format.dateRenderer(Date.patterns.ISO8601Long),
                                        dataIndex: 'created'
                                    },

                                    {
                                        header   : i18n.accounts.email,
                                        width    : 115,
                                        sortable : true,
                                        dataIndex: 'email',
                                        filter: {
                                            type: 'string'
                                        }

                                    },
                                ],
                                listeners: {/*
                                    render:function(){
                                     this.bbar.updateInfo();
                                    }*/
                                },
                                stripeRows: true,
                                title: i18n.accounts.accounts,
                                stateful: true,
                                stateId: 'accountsgrid',
                                
                            //bbar:this.pagination
                });
            this.bbar.store = this.store;
            this.on('rowdblclick', function(eventGrid, rowIndex, e) {
            	this.tbFormInTabCallBack(this, 'edit_user',this.selModel.selections.items[0].id);
            	
            	}, this);            
            EBS.conponents.accountsGrid.superclass.initComponent.apply(this, arguments);
            //this.bbar.updateInfo();

         } //initComponent
     });


/* ACCOUNTS FORMS*/
    EBS.forms.ebs_accountsPanel.edit_user = {
                                        xtype: 'form',
                                        //id: 'account-info',
                                        windowTitle:'Account details',
                                        autoScroll:true,
                                        layout:'fit',
                                        url:'/ebsadmin/account/', 
                                        save_url:'/ebsadmin/account/save/',
                                        standardSubmit: false,
                                        frame:false,
                                        border:false,
                                        method:'POST',
                                        
                                        reader: new Ext.data.JsonReader({
                                            idProperty: 'id',          
                                            root: 'records',             
                                            fields: [
                                                {name: 'allow_webcab', type:'boolean'},
												{name: 'house', type:'int'},
												{name: 'street', type:'int'},
												{name: 'postcode', type:'int'},
												{name: 'suspended', type:'int'},
												{name: 'id', type:'int'},
												{name: 'city', type:'int'},
												{name: 'password', type:'string'},
												{name: 'ballance', type:'float'},
												{name: 'email', type:'string'},
												{name: 'username', type:'string'},
												{name: 'entrance', type:'string'},
												{name: 'vlan', type:'int'},
												{name: 'allow_expresscards', type:'boolean'},
												{name: 'disabled_by_limit', type:'boolean'},
												{name: 'balance_blocked', type:'boolean'},
												{name: 'room', type:'string'},
												{name: 'created', type:'date', dateFormat: Date.patterns.ISO8601Long},
												{name: 'region', type:'string'},
												{name: 'credit', type:'float'},
												{name: 'ipn_status', type:'boolean'},
												{name: 'house_bulk', type:'string'},
												{name: 'fullname', type:'string'},
												{name: 'passport', type:'string'},
												{name: 'passport_given', type:'string'},
												{name: 'phone_h', type:'string'},
												{name: 'phone_m', type:'string'},
												{name: 'contactperson_phone', type:'string'},
												{name: 'comment', type:'string'},
												{name: 'row', type:'int'},
												{name: 'elevator_direction', type:'string'},
												{name: 'contactperson', type:'string'},
												{name: 'status', type:'int'},
												{name: 'passport_date', type:'string'},
												{name: 'contract' , type:'string'},
												{name: 'systemuser', type:'int'},
												{name: 'last_balance_null', type:'date', dateFormat: Date.patterns.ISO8601Long},
												{name: 'entrance_code', type:'string'},
												{name: 'private_passport_number', type:'string'},
												{name: 'allow_ipn_with_null', type:'boolean'},
												{name: 'allow_ipn_with_minus', type:'boolean'},
												{name: 'allow_ipn_with_block', type:'boolean'},
                                            ]
                                        }),     
                                        items:{
                                            //id:'edit_user_form',
                                            xtype: 'tabpanel',
                                            activeTab: 0,
                                            //width: 600,
                                            //height: 250,
                                            plain: true,
                                            
                                            defaults :{
                                                autoScroll: true,
                                                bodyPadding: 10
                                            },
                                            items: [{
                                                xtype: 'container',
                                                autoScroll: true,
                                                
                                                title:'Учётные данные',
                                                layout: 'column',
                                                animCollapse: false,
                                                frame:false,
                                                border:false,                                                
                                                bodyStyle: {
                                                    padding: '5px 5px 5px 5px'
                                                },

                                                items: [
                                                    {
                                                        xtype: 'container',
                                                        width: 420,
                                                        layout: 'anchor',
                                                        items: [
                                                            {
                                                                xtype: 'fieldset',
                                                                height: 139,
                                                                width: 400,
                                                                title: 'Учётные данные',
                                                                items: [
																	{
																	    xtype: 'hidden',
																	    name: 'id',
																	},
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'username',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Логин'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'password',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Пароль'
                                                                    },
                                                                    {
                                                                        xtype: 'xdatetime',
                                                                        name: 'created',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Дата создания'
                                                                    },
                                                                    {
                                                                        xtype: 'container',
                                                                        width: 472,
                                                                        forceLayout: true,
                                                                        layout: 'hbox',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Номер договора',
                                                                        pack: 'center',
                                                                        items: [
                                                                            {
                                                                                xtype: 'combo',
                                                                                flex: 1
                                                                            },
                                                                            {
                                                                                xtype: 'button',
                                                                                text: 'Печать',
                                                                                flex: 1
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'fieldset',
                                                                height: 609,
                                                                width: 400,
                                                                title: 'Данные аккаунта',
                                                                labelWidth: 140,
                                                                items: [
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'contactperson',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Контактное лицо'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Контактный телефон'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'fullname',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'ФИО'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'email',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'E-mail'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'phone_h',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Дом. телефон'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'phone_m',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Моб. телефон'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'passport',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Паспорт №'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'private_passport_number',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Личный номер'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'passport_given',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Кем выдан'
                                                                    },
                                                                    {
                                                                        xtype: 'datefield',
                                                                        name: 'passport_date',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Когда выдан'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'postcode',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Район'
                                                                    },
                                                                    {
                                                                        xtype: 'xcombocity',
                                                                        name: 'city',
                                                                        hiddenName: "city",
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Город',
                                                                        listeners:{
                                                                        	select: function(combo, record, index) {
                                                                        		
                                                                        		this.findParentByType('form').getForm().findField('street').clearValue();
																				this.findParentByType('form').getForm().findField('street').store.load({params:{city_id: this.value}});
                                                                        		
                                                                              },
                                                                       },
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'region',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Подъезд'
                                                                    },
                                                                    {
                                                                        xtype: 'xcombostreet',
                                                                        name: 'street',
                                                                        //id:'street',
                                                                        hiddenName: "street",
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Улица',
                                                                        listeners:{
                                                                        	select: function(combo, record, index) {
                                                                        		
                                                                        		this.findParentByType('form').getForm().findField("house").clearValue();
																				this.findParentByType('form').getForm().findField("house").store.load({params:{street_id: this.value}});                                                                              },
                                                                       

                                                                        },
		                                                                  
                                                                    },
                                                                    {
                                                                        xtype: 'xcombohouse',
                                                                        name: 'house',
                                                                        //id:'house',
                                                                        hiddenName: "house",
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Дом'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'house_bulk',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Корпус'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Подъезд'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'entrance_code',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Код домофона'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'row',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Этаж'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'elevator_direction',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Направление от лифта'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'room',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Квартира'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        xtype: 'container',
                                                        layout: 'anchor',
                                                        items: [
                                                            {
                                                                xtype: 'fieldset',
                                                                height: 139,
                                                                width: 410,
                                                                padding: '',
                                                                title: 'Баланс',
                                                                items: [
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'ballance',
                                                                        anchor: '100%',
                                                                        disabled: true,
                                                                        fieldLabel: 'Баланс'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'credit',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Кредит'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'max_credit',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Кредит доверия'
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'fieldset',
                                                                stateful: true,
                                                                height: 359,
                                                                width: 410,
                                                                animCollapse: true,
                                                                collapsible: true,
                                                                title: 'Юр. лицо',
                                                                items: [
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'organization_name',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Название'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'uraddress',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Юр. адрес'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'okpo',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'ОКПО'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'unp',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'УНП'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'organization_phone',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Телефон'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'organization_fax',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Факс'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'organization_kpp',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'КПП'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'kor_s',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Корр. счёт'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'bank_name',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Банк'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'bankcode',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Код банка'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'rs',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Расчётный счёт'
                                                                    },
                                                                    {
                                                                        xtype: 'textfield',
                                                                        name: 'currency',
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Валюта'
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                xtype: 'fieldset',
                                                                height: 179,
                                                                width: 410,
                                                                title: 'Параметры',
                                                                items: [
                                                                    {
                                                                        xtype: 'xcomboaccountstatus',
                                                                        name: 'status',
                                                                        hiddenName: "status",
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Статус',
                                                                       
                                                                    },
                                                                    {
                                                                        xtype: 'xcombosystemuser',
                                                                        name: 'systemuser',
                                                                        hiddenName: "systemuser",
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Персональный менеджер'
                                                                    },
                                                                    {
                                                                        xtype: 'combo',
                                                                        name: 'group',
                                                                        hiddenName: "group",
                                                                        anchor: '100%',
                                                                        fieldLabel: 'Группа'
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                                },
                                                {
                                                    xtype: 'container',
                                                    title: 'group',
                                                
                                                },
                                                ]



                                           }
    								//form.load({url:'/account/', method:'GET',params:{'id':selection.items[0].id}} );
                                      };
    EBS.forms.ebs_accountsPanel.edit_user_submitAction =  function(object, event){
        //form = object.ownerCt;
        //console.log(form);
    }
    
    var win = new Ext.Window({
        id:'popcombo-win'
       ,title:''
       ,layout:'fit'
       ,closable:true
       ,border:false
       ,height: 226
       ,width: 420
       ,items:{
           xtype: 'form',
           
           layout: 'table',
    	   layoutConfig:{ 
    	       columns: 4,
    	       tableStyle: 'border-spacing: 25px;'
    	   }, 
    	   defaults : {                                                        
    	      height:30, 
    	       width:150,

    	   },
           title: 'Выберите период',
           columns: 4,
           items: [
               {
                   xtype: 'radio',
                   boxLabel: 'Квартал'
               },
               {
                   xtype: 'combo',
                   padding:'5px',

               },
               {
                   xtype: 'combo',

               },
               {
                   xtype: 'label',

                   text: 'года',
               },
               {
                   xtype: 'radio',
                   boxLabel: 'Месяц'
               },
               {
                   xtype: 'combo',

               },
               {
                   xtype: 'combo',

               },
               {
                   xtype: 'label',
                   text: 'года'
               },
               {
                   xtype: 'radio',
                   boxLabel: 'День'
               },
               {
                   xtype: 'datefield',
                   colspan:3,
               },
             
               {
                   xtype: 'radio',
                   boxLabel: 'Период'
               },
               {
                   xtype: 'datefield'
               },
               {
                   xtype: 'datefield',
                   colspan:2,
                	   
               },
               {
                   xtype: 'radio',
                   boxLabel: 'Этот месяц',
                   colspan:4,
               },
               {
                   xtype: 'radio',
                   boxLabel: 'Эта неделя',
                   colspan:4,
                	   
                	   
               },
            
               {
                   xtype: 'button',
                   text: 'Выбрать'
               }
           ]
       }
   });

   //win.show();

    EBS.forms.ebs_accountsPanel.edit_credit = {
                                        xtype: 'form',
                                        id: 'account-credit',
                                        windowTitle:'Платёж',
                                        items:{
                                            xtype: 'panel',
                                            autoHeight: true,
                                            //height: 316,
                                            //width: 462,
                                            padding:'5px',
                                            layout: 'anchor',
                                            //title: 'Проведение платежа',
                                            items: [
                                                {
                                                    xtype: 'fieldset',
                                                    autoHeight: false,
                                                    autoWidth: false,
                                                    //height: 231,
                                                    title: 'Параметры платежа',
                                                    labelWidth: 150,
                                                    items: [{
                                                    		xtype:'xtrtypecombo',
                                                    		name:'transaction_type_id',
                                                    		id:'transaction_type_id',
                                                    	},
                                                        
                                                        {
                                                            xtype: 'numberfield',
                                                            name: 'summ',
                                                            anchor: '100%',
                                                            fieldLabel: 'Сумма'
                                                        },
                                                        {
                                                            xtype: 'textfield',
                                                            name: 'document',
                                                            anchor: '100%',
                                                            fieldLabel: 'Документ'
                                                        },
                                                        {
                                                            xtype: 'textfield',
                                                            name: 'description',
                                                            anchor: '100%',
                                                            fieldLabel: 'Комментарий'
                                                        },
                                                        {
                                                            xtype: 'datefield',
                                                            name: 'created',
                                                            anchor: '100%',
                                                            fieldLabel: 'Дата'
                                                        },
                                                        {
                                                            xtype: 'checkbox',
                                                            boxLabel: 'Да',
                                                            anchor: '100%',
                                                            fieldLabel: 'Обещанный платёж'
                                                        },
                                                        {
                                                            xtype: 'compositefield',
                                                            anchor: '100%',
                                                            fieldLabel: 'Истекает',
                                                            items: [
                                                                {
                                                                    xtype: 'datefield',
                                                                    width: 212
                                                                },
                                                                {
                                                                    xtype: 'checkbox',
                                                                    boxLabel: 'Никогда',
                                                                    fieldLabel: 'Label'
                                                                }
                                                            ]
                                                        }
                                                        
                                                    ]
                                                },
                                                {
                                                    xtype: 'container',
                                                    height: 29,
                                                    width: 449,
                                                    layout: 'column',
                                                    items: [
                                                        {
                                                            xtype: 'button',
                                                            width: 131,
                                                            text: 'Зачислить'
                                                        },
                                                        {
                                                            xtype: 'button',
                                                            width: 157,
                                                            text: 'Печать'
                                                        },
                                                        {
                                                            xtype: 'button',
                                                            width: 158,
                                                            text: 'Закрыть'
                                                        }
                                                    ]
                                                }
                                                
                                                
                                            ]
    
                                        }
    									
                                      }
    EBS.forms.ebs_accountsPanel.edit_credit_submitAction =  function(object, event){
        form = object.ownerCt;
        //console.log(form);
    }
/* EOF ACCOUNTS FORMS*/

    Ext.reg("ebs_accountsPanel", EBS.conponents.accountsGrid);
    EBS.windows.keys[EBS.windows.keys.length] = 'ebs_accountsPanel';
});