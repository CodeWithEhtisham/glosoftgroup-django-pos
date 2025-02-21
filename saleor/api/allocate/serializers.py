from django.utils.formats import localize
from rest_framework.serializers import (
                HyperlinkedIdentityField,
                SerializerMethodField,
                ValidationError,
                )

from rest_framework import serializers
from django.contrib.auth import get_user_model
from ...sale.models import (
            Terminal,
            )
from ...allocate.models import Allocate, AllocatedItem
from ...product.models import (
            ProductVariant,
            Stock,
            )
from decimal import Decimal
from structlog import get_logger

logger = get_logger(__name__)
User = get_user_model()


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllocatedItem
        fields = (
                'id',
                'order',
                'sku',
                'stock_id',
                'allocated_quantity',
                'quantity',
                'sold',
                'unsold',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'tax',
                'discount',
                 )


class ItemsSerializer(serializers.ModelSerializer):
    available_stock = SerializerMethodField()
    item_pk = SerializerMethodField()

    class Meta:
        model = AllocatedItem
        fields = (
                'id',
                'order',
                'sku',
                'stock_id',
                'quantity',
                'sold',
                'unsold',
                'allocated_quantity',
                'unit_cost',
                'total_cost',
                'product_name',
                'product_category',
                'available_stock',
                'item_pk',
                'tax',
                'discount',
                 )

    def get_item_pk(self,obj):
        return obj.pk

    def get_available_stock(self,obj):
        try:
            stock = ProductVariant.objects.get(sku=obj.sku)
            return stock.get_stock_quantity()
        except:
            return 0


class CarAllocateListSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='allocate-api:update-allocate')
    car_url = HyperlinkedIdentityField(view_name='dashboard:car_transfer_list')
    allocated_items = ItemsSerializer(many=True)
    allocate_status = SerializerMethodField()
    cashier = SerializerMethodField()
    car_name = SerializerMethodField()
    date = SerializerMethodField()
    total_allocated = SerializerMethodField()
    total_sold = SerializerMethodField()
    car_total_net = SerializerMethodField()
    agent_name = SerializerMethodField()

    class Meta:
        model = Allocate
        fields = (
            'id',
            'user',
            'invoice_number',
            'total_net',
            'sub_total',
            'update_url',
            'car_url',
            'balance',
            'terminal',
            'amount_paid',
            'agent_name',
            'car_name',
            'mobile',
            'customer_name',
            'cashier',
            'allocate_status',
            'total_tax',
            'discount_amount',
            'due_date',
            'date',
            'allocated_items',
            'total_allocated',
            'total_sold',
            'car_total_net'
        )

    def get_car_total_net(self, obj):
        return "{:,}".format(Allocate.objects.car_total_net(obj))

    def get_total_allocated(self, obj):
        return "{:,}".format(Allocate.objects.total_allocated(obj,self.context['date']))

    def get_total_sold(self, obj):
        return "{:,}".format(Allocate.objects.total_sold(obj))

    def get_date(self, obj):
        return localize(obj.created)

    def get_agent_name(self, obj):
        return obj.agent.name

    def get_car_name(self, obj):
        try:
            return str(obj.car.name)+' ('+str(obj.car.number)+')'
        except Exception as e:
            return ''

    def get_allocate_status(self, obj):
        if obj.status == 'payment-pending':
            return '<span class="badge badge-flat border-warning text-warning-600" > Pending..</span>'
        return '<span class ="text-success  icon-checkmark-circle" > <i> </i> </span>'

    def get_cashier(self, obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name


class AllocateListSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='allocate-api:update-allocate')
    car_allocate_url = HyperlinkedIdentityField(view_name='dashboard:car-allocate-detail')
    allocated_items = ItemsSerializer(many=True)
    cashier = SerializerMethodField()
    total_allocated = SerializerMethodField()
    total_sold = SerializerMethodField()
    agent_name = SerializerMethodField()
    allocate_status = SerializerMethodField()
    date = SerializerMethodField()

    class Meta:
        model = Allocate
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'update_url',
                 'car_allocate_url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'agent',
                 'agent_name',
                 'car',
                 'mobile',
                 'customer_name',
                 'cashier',
                 'status',
                 'total_tax',
                 'discount_amount',
                 'due_date',
                 'debt',
                 'total_allocated',
                 'total_sold',
                 'allocate_status',
                 'date',
                 'allocated_items'
                )

    def get_date(self, obj):
        return localize(obj.created)

    def get_allocate_status(self, obj):
        if obj.status == 'payment-pending':
            return '<span class="badge badge-flat border-warning text-warning-600" > Pending..</span>'
        return '<span class ="text-success  icon-checkmark-circle" > <i> </i> </span>'

    def get_cashier(self, obj):
        name = User.objects.get(pk=obj.user.id)
        return name.name

    def get_total_allocated(self, obj):
        return obj.total_allocated()

    def get_total_sold(self, obj):
        return obj.sold_items()

    def get_agent_name(self, obj):
        return obj.agent.name


class CreateAllocateSerializer(serializers.ModelSerializer):
    update_url = HyperlinkedIdentityField(view_name='allocate-api:update-allocate')
    allocated_items = TrackSerializer(many=True)

    class Meta:
        model = Allocate
        fields = (
                 'id',
                 'user',
                 'invoice_number',
                 'total_net',
                 'sub_total',                 
                 'update_url',
                 'balance',
                 'terminal',
                 'amount_paid',
                 'agent',
                 'car',
                 'mobile',
                 'customer_name',
                 'status',
                 'total_tax',
                 'allocated_items',
                )

    def validate_total_net(self,value):
        data = self.get_initial()        
        try:
            self.total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')
        return value
        
    def validate_terminal(self,value):
        data = self.get_initial()
        self.terminal_id = int(data.get('terminal'))
        self.l=[]
        terminals = Terminal.objects.all()
        for term in terminals:
            self.l.append(term.pk)
        if not self.terminal_id in self.l:      
            raise ValidationError('Terminal specified does not exist')
        return value    

    def create(self, validated_data):
        try:
           total_net = Decimal(validated_data.get('total_net'))
        except:
           total_net = Decimal(0)
        solditems_data = validated_data.pop('allocated_items')
        credit = Allocate.objects.create(
                                     user=validated_data.get('user'),
                                     invoice_number=validated_data.get('invoice_number'),
                                     total_net=validated_data.get('total_net'),
                                     sub_total=validated_data.get('sub_total'),
                                     balance=validated_data.get('balance'),
                                     terminal=validated_data.get('terminal'),
                                     amount_paid=validated_data.get('amount_paid'),
                                     agent=validated_data.get('agent'),
                                     car=validated_data.get('car'),
                                     status='payment-pending',
                                     mobile=validated_data.get('mobile'),
                                     debt=validated_data.get('total_net'),
                                     customer_name=validated_data.get('customer_name'))
        for solditem_data in solditems_data:
            item_temp = AllocatedItem.objects.create(allocate=credit, **solditem_data)
            item = item_temp
            item_temp.delete()
            carry = int(solditem_data['allocated_quantity'])
            checker = True
            while checker:
                stock = Stock.objects.filter(variant__sku=solditem_data['sku']).first()
                if stock:
                    item.id = None
                    if stock.quantity > 0:
                        if carry >= stock.quantity:
                            try:
                                item.unit_purchase = stock.cost_price.gross
                            except:
                                pass
                            try:
                                item.total_purchase = stock.cost_price.gross * Decimal(stock.quantity)
                            except:
                                pass
                            item.stock_id = stock.pk
                            item.allocated_quantity = stock.quantity
                            item.minimum_price = stock.minimum_price.gross
                            item.wholesale_override = stock.wholesale_override.gross
                            item.low_stock_threshold = stock.low_stock_threshold
                            item.unit_cost = stock.price_override.gross
                            item.total_cost = stock.price_override.gross * stock.quantity
                            item.save()
                            carry -= stock.quantity
                            stock.delete()
                            if carry <= 0:
                                checker = False
                        else:
                            # Stock.objects.decrease_stock(stock, carry)
                            stock.quantity -= carry
                            stock.save()
                            try:
                                item.unit_purchase = stock.cost_price.gross
                            except:
                                pass
                            try:
                                item.total_purchase = stock.cost_price.gross * Decimal(carry)
                            except:
                                pass
                            item.stock_id = stock.pk
                            item.allocated_quantity = carry
                            item.minimum_price = stock.minimum_price.gross
                            item.wholesale_override = stock.wholesale_override.gross
                            item.low_stock_threshold = stock.low_stock_threshold
                            item.unit_cost = stock.price_override.gross
                            item.total_cost = stock.price_override.gross * carry

                            item.save()

                            checker = False
                    else:
                        stock.delete()
                        checker = False
                else:
                    print('stock not found')
                    checker = False
            # try:
            #     stock = Stock.objects.get(variant__sku=solditem_data['sku'])
            #     if stock:
            #         Stock.objects.decrease_stock(stock,solditem_data['allocated_quantity'])
            #         print stock.quantity
            #     else:
            #         print('stock not found')
            # except Exception as e:
            #     logger.error(e)
                
        return credit


class AllocateUpdateSerializer(serializers.ModelSerializer):
    allocated_items = TrackSerializer(many=True)

    class Meta:
        model = Allocate
        fields = (
                 'id',
                 'invoice_number',
                 'total_net',
                 'sub_total',                
                 'balance',
                 'terminal',
                 'amount_paid',                 
                 'mobile',
                 'customer_name',
                 'status',
                 'total_tax',
                 'discount_amount',
                 'debt',
                 'allocated_items',
                 )

    def validate_total_net(self, value):
        data = self.get_initial()        
        try:
            total_net = Decimal(data.get('total_net'))
        except:
            raise ValidationError('Total Net should be a decimal/integer')

    def validate_debt(self, value):
        data = self.get_initial()        
        try:
            debt = Decimal(data.get('debt'))
        except:
            raise ValidationError('Debt should be a decimal/integer')
        return value

    def validate_amout_paid(self,value):
        data = self.get_initial()        
        try:
            amount_paid = Decimal(data.get('amount_paid'))
        except:
            raise ValidationError('Amount paid should be a decimal/integer')
        return value

    def update(self, instance, validated_data):
        terminal = Terminal.objects.get(pk=instance.terminal_id)
        for x in validated_data.get('allocated_items'):
            # get old stock
            old = instance.item_detail(x['stock_id'])
            old.sold += x['quantity']
            old.quantity = x['quantity']
            old.total_cost = x['total_cost']
            unsold = old.allocated_quantity - old.sold
            old.unsold = unsold

            # handle return unsold product to stock
            if validated_data.get('status', instance.status) == 'fully-paid':
                try:
                    stock = Stock.objects.get(pk=x['stock_id'])
                    stock.quantity += unsold
                    stock.save()
                except Exception as e:
                    if unsold > 0:
                        variant = ProductVariant.objects.get(sku=x['sku'])
                        Stock.objects.create(
                            variant=variant,
                            price_override=old.unit_cost,
                            wholesale_override=old.wholesale_override,
                            minimum_price=old.minimum_price,
                            low_stock_threshold=old.low_stock_threshold,
                            cost_price=old.unit_purchase,
                            quantity=unsold)
                    print('stock not found. Recreated new stock')
            old.save()

        terminal.amount += Decimal(validated_data.get('amount_paid', instance.amount_paid))       
        terminal.save()        
        instance.debt = instance.debt-validated_data.get('amount_paid', instance.amount_paid)
        instance.total_sale += validated_data.get('amount_paid', instance.amount_paid)

        instance.amount_paid = validated_data.get('amount_paid', instance.amount_paid)

        instance.status = validated_data.get('status', instance.status)

        instance.mobile = validated_data.get('mobile', instance.mobile)   
        
        instance.customer_name = validated_data.get('customer_name', instance.customer_name)
        instance.save()        
        return instance


