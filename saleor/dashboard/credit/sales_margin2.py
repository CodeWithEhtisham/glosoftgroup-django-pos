
from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.db.models import Count, Sum, Q
from ...utils import image64

from django.core.paginator import Paginator, EmptyPage, InvalidPage, PageNotAnInteger
import datetime
from django.utils.dateformat import DateFormat
import logging

from ...utils import render_to_pdf
from datetime import date

from ..views import staff_member_required
from ...sale.models import Sales, SoldItem
from ...product.models import ProductVariant
from ...decorators import permission_decorator, user_trail

from structlog import get_logger

logger = get_logger(__name__)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_list(request):
    try:
        try:
            last_sale = Sales.objects.latest('id')
            last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
        except:
            last_date_of_sales = DateFormat(datetime.datetime.today()).format('Y-m-d')

        all_sales = Sales.objects.filter(created__contains=last_date_of_sales)
        total_sales_amount = all_sales.aggregate(Sum('total_net'))
        total_tax_amount = all_sales.aggregate(Sum('total_tax'))
        total_sales = []
        costPrice = []
        for sale in all_sales:
            quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
            setattr(sale, 'quantity', quantity['c'])
            for i in SoldItem.objects.filter(sales=sale):
                product = ProductVariant.objects.get(sku=i.sku)
                try:
                    quantity = product.get_cost_price().gross
                except:
                    quantity = product.get_cost_price()
                costPrice.append(quantity)
            totalCostPrice = sum(costPrice)
            setattr(sale, 'totalCostPrice', totalCostPrice)
            try:
                grossProfit = sale.total_net - totalCostPrice
                margin = round((grossProfit / sale.total_net) * 100, 2)
            except:
                grossProfit = 0
                margin = 0
            setattr(sale, 'margin', margin)
            total_sales.append(sale)

        try:
            grossProfit = total_sales_amount['total_net__sum'] - totalCostPrice
            totalMargin = round((grossProfit / total_sales_amount['total_net__sum']) * 100, 2)
        except:
            grossProfit = 0
            totalMargin = 0

        page = request.GET.get('page', 1)
        paginator = Paginator(total_sales, 10)
        try:
            total_sales = paginator.page(page)
        except PageNotAnInteger:
            total_sales = paginator.page(1)
        except InvalidPage:
            total_sales = paginator.page(1)
        except EmptyPage:
            total_sales = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed sales reports', 'view')
        logger.info('User: ' + str(request.user.name) + ' accessed the view sales report page')
        data = {
            'pn': paginator.num_pages,
            'sales': total_sales,
            "total_sales_amount": total_sales_amount,
            "total_tax_amount": total_tax_amount,
            "date": last_date_of_sales,
            "totalMargin": totalMargin
        }
        return TemplateResponse(request, 'dashboard/reports/sales_margin2/sales_list.html', data)
    except Exception as e:
        logger.error(e)
        print (e)


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_detail(request, pk=None):
    try:
        sale = Sales.objects.get(pk=pk)
        items = SoldItem.objects.filter(sales=sale)
        total_items = []
        for t in items:
            product = ProductVariant.objects.get(sku=t.sku)
            try:
                itemPrice = product.get_cost_price().gross
            except:
                itemPrice = product.get_cost_price()
            unitSalesCost = t.unit_cost
            totalSalesCost = t.total_cost
            try:
                grossProfit = unitSalesCost - itemPrice
                unitMargin = round((grossProfit / unitSalesCost) * 100, 2)
                salesGrossProfit = totalSalesCost - (itemPrice * t.quantity)
                salesMargin = round((salesGrossProfit / totalSalesCost) * 100, 2)
            except:
                grossProfit = 0
                unitMargin = 0
                salesMargin = 0
            setattr(t, 'unitMargin', unitMargin)
            setattr(t, 'salesMargin', salesMargin)
            total_items.append(t)
        data = {'items': total_items, "sale": sale}
        return TemplateResponse(request, 'dashboard/reports/sales_margin2/details.html', data)
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
def sales_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    date = request.GET.get('gid')
    sales = Sales.objects.all().order_by('-id')
    today_formart = DateFormat(datetime.date.today())
    today = today_formart.format('Y-m-d')
    ts = Sales.objects.filter(created__icontains=today)
    tsum = ts.aggregate(Sum('total_net'))
    total_sales = Sales.objects.aggregate(Sum('total_net'))
    total_tax = Sales.objects.aggregate(Sum('total_tax'))

    if date:
        try:
            all_salesd = Sales.objects.filter(created__icontains=date).order_by('-id')
            that_date_sum = Sales.objects.filter(created__contains=date).aggregate(Sum('total_net'))
            sales = []
            costPrice = []
            for sale in all_salesd:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                for i in SoldItem.objects.filter(sales=sale):
                    product = ProductVariant.objects.get(sku=i.sku)
                    try:
                        quantity = product.get_cost_price().gross
                    except:
                        quantity = product.get_cost_price()
                    costPrice.append(quantity)
                totalCostPrice = sum(costPrice)
                setattr(sale, 'totalCostPrice', totalCostPrice)
                try:
                    grossProfit = sale.total_net - totalCostPrice
                    status = 'true'
                    margin = round((grossProfit / sale.total_net) * 100, 2)
                except:
                    grossProfit = 0
                    margin = 0
                setattr(sale, 'margin', margin)
                sales.append(sale)

            if p2_sz and date:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/paginate.html',
                                        {'sales': sales, 'gid': date})

            paginator = Paginator(sales, 10)
            sales = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/p2.html',
                                    {'sales': sales, 'pn': paginator.num_pages, 'sz': 10, 'gid': date,
                                     'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum,
                                     'that_date_sum': that_date_sum, 'date': date, 'today': today})

        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/p2.html', {'date': date})

    else:
        try:
            last_sale = Sales.objects.latest('id')
            last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
            all_sales = Sales.objects.filter(created__contains=last_date_of_sales)
            total_sales_amount = all_sales.aggregate(Sum('total_net'))
            total_tax_amount = all_sales.aggregate(Sum('total_tax'))
            sales = []
            costPrice = []
            for sale in all_sales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                for i in SoldItem.objects.filter(sales=sale):
                    product = ProductVariant.objects.get(sku=i.sku)
                    try:
                        quantity = product.get_cost_price().gross
                    except:
                        quantity = product.get_cost_price()
                    costPrice.append(quantity)
                totalCostPrice = sum(costPrice)
                setattr(sale, 'totalCostPrice', totalCostPrice)
                try:
                    grossProfit = sale.total_net - totalCostPrice
                    status = 'true'
                    margin = round((grossProfit / sale.total_net) * 100, 2)
                except:
                    grossProfit = 0
                    margin = 0
                setattr(sale, 'margin', margin)
                sales.append(sale)

            if list_sz:
                paginator = Paginator(sales, int(list_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/p2.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                         'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum})
            else:
                paginator = Paginator(sales, 10)
            if p2_sz:
                paginator = Paginator(sales, int(p2_sz))
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/paginate.html', {'sales': sales})

            try:
                sales = paginator.page(page)
            except PageNotAnInteger:
                sales = paginator.page(1)
            except InvalidPage:
                sales = paginator.page(1)
            except EmptyPage:
                sales = paginator.page(paginator.num_pages)
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/paginate.html', {'sales': sales})
        except ObjectDoesNotExist as e:
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/p2.html', {'date': date})


@staff_member_required
def sales_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            all_sales = Sales.objects.filter(
                Q(invoice_number__icontains=q) |
                Q(terminal__terminal_name__icontains=q) |
                Q(created__icontains=q) |
                Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
                Q(solditems__product_name__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__name__icontains=q)).order_by('id').distinct()
            sales = []
            costPrice = []

            if request.GET.get('gid'):
                csales = all_sales.filter(created__icontains=request.GET.get('gid'))
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    for i in SoldItem.objects.filter(sales=sale):
                        product = ProductVariant.objects.get(sku=i.sku)
                        try:
                            quantity = product.get_cost_price().gross
                        except:
                            quantity = product.get_cost_price()
                        costPrice.append(quantity)
                    totalCostPrice = sum(costPrice)
                    setattr(sale, 'totalCostPrice', totalCostPrice)
                    try:
                        grossProfit = sale.total_net - totalCostPrice
                        status = 'true'
                        margin = round((grossProfit / sale.total_net) * 100, 2)
                    except:
                        grossProfit = 0
                        margin = 0
                    setattr(sale, 'margin', margin)
                    sales.append(sale)

                if p2_sz:
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales_margin2/paginate.html', {'sales': sales})

                if list_sz:
                    paginator = Paginator(sales, int(list_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales_margin2/search.html',
                                            {'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz,
                                             'gid': request.GET.get('gid'), 'q': q})

                paginator = Paginator(sales, 10)
                sales = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/search.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': sz,
                                         'gid': request.GET.get('gid')})

            else:
                for sale in all_sales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    for i in SoldItem.objects.filter(sales=sale):
                        product = ProductVariant.objects.get(sku=i.sku)
                        try:
                            quantity = product.get_cost_price().gross
                        except:
                            quantity = product.get_cost_price()
                        costPrice.append(quantity)
                    totalCostPrice = sum(costPrice)
                    setattr(sale, 'totalCostPrice', totalCostPrice)
                    try:
                        grossProfit = sale.total_net - totalCostPrice
                        status = 'true'
                        margin = round((grossProfit / sale.total_net) * 100, 2)
                    except:
                        grossProfit = 0
                        margin = 0
                    setattr(sale, 'margin', margin)
                    sales.append(sale)

                if list_sz:
                    paginator = Paginator(sales, int(list_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales_margin2/search.html',
                                            {'sales': sales, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                             'q': q})

                if p2_sz:
                    paginator = Paginator(sales, int(p2_sz))
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales_margin2/paginate.html', {'sales': sales})

                paginator = Paginator(sales, 10)
                try:
                    sales = paginator.page(page)
                except PageNotAnInteger:
                    sales = paginator.page(1)
                except InvalidPage:
                    sales = paginator.page(1)
                except EmptyPage:
                    sales = paginator.page(paginator.num_pages)
                if p2_sz:
                    sales = paginator.page(page)
                    return TemplateResponse(request, 'dashboard/reports/sales_margin2/paginate.html', {'sales': sales})

                return TemplateResponse(request, 'dashboard/reports/sales_margin2/search.html',
                                        {'sales': sales, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def sales_reports(request):
    try:
        today = datetime.date.today()
        items = SoldItem.objects.all().order_by('-id')
        ts = Sales.objects.filter(created__icontains=today)
        tsum = ts.aggregate(Sum('total_net'))
        total_sales = Sales.objects.aggregate(Sum('total_net'))
        total_tax = Sales.objects.aggregate(Sum('total_tax'))
        page = request.GET.get('page', 1)
        paginator = Paginator(items, 10)
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except InvalidPage:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages)
        user_trail(request.user.name, 'accessed sales reports', 'view')
        logger.info('User: ' + str(request.user.name) + ' accessed the view sales report page')
        if request.GET.get('initial'):
            return HttpResponse(paginator.num_pages)
        else:
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/sales.html',
                                    {'items': items, 'total_sales': total_sales, 'total_tax': total_tax, 'ts': ts,
                                     'tsum': tsum})
    except TypeError as e:
        logger.error(e)
        return HttpResponse('error accessing sales reports')


@staff_member_required
@permission_decorator('reports.view_sale_reports')
def pdf_sale_tax_detail(request, pk=None):
    try:
        sale = Sales.objects.get(pk=pk)
        items = SoldItem.objects.filter(sales=sale)
        total_items = []
        for t in items:
            product = ProductVariant.objects.get(sku=t.sku)
            try:
                itemPrice = product.get_cost_price().gross
            except:
                itemPrice = product.get_cost_price()
            unitSalesCost = t.unit_cost
            totalSalesCost = t.total_cost
            try:
                grossProfit = unitSalesCost - itemPrice
                unitMargin = round((grossProfit / unitSalesCost) * 100, 2)
                salesGrossProfit = totalSalesCost - (itemPrice * t.quantity)
                salesMargin = round((salesGrossProfit / totalSalesCost) * 100, 2)
            except:
                grossProfit = 0
                unitMargin = 0
                salesMargin = 0
            setattr(t, 'unitMargin', unitMargin)
            setattr(t, 'salesMargin', salesMargin)
            total_items.append(t)
        img = image64()
        data = {
            'today': date.today(),
            'items': total_items,
            'sale': sale,
            'puller': request.user,
            'image': img
        }
        pdf = render_to_pdf('dashboard/reports/sales_margin2/pdf/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
    except ObjectDoesNotExist as e:
        logger.error(e)


@staff_member_required
def sales_list_tax_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        sales = []
        costPrice = []
        if q is not None:
            all_sales = Sales.objects.filter(
                Q(invoice_number__icontains=q) |
                Q(terminal__terminal_name__icontains=q) |
                Q(created__icontains=q) |
                Q(customer__name__icontains=q) | Q(customer__mobile__icontains=q) |
                Q(solditems__product_name__icontains=q) |
                Q(user__email__icontains=q) |
                Q(user__name__icontains=q)).order_by('id').distinct()

            if gid:
                csales = all_sales.filter(created__icontains=gid)
                for sale in csales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    for i in SoldItem.objects.filter(sales=sale):
                        product = ProductVariant.objects.get(sku=i.sku)
                        try:
                            quantity = product.get_cost_price().gross
                        except:
                            quantity = product.get_cost_price()
                        costPrice.append(quantity)
                    totalCostPrice = sum(costPrice)
                    setattr(sale, 'totalCostPrice', totalCostPrice)
                    try:
                        grossProfit = sale.total_net - totalCostPrice
                        status = 'true'
                        margin = round((grossProfit / sale.total_net) * 100, 2)
                    except:
                        grossProfit = 0
                        margin = 0
                    setattr(sale, 'margin', margin)
                    sales.append(sale)
            else:
                for sale in all_sales:
                    quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                    setattr(sale, 'quantity', quantity['c'])
                    for i in SoldItem.objects.filter(sales=sale):
                        product = ProductVariant.objects.get(sku=i.sku)
                        try:
                            quantity = product.get_cost_price().gross
                        except:
                            quantity = product.get_cost_price()
                        costPrice.append(quantity)
                    totalCostPrice = sum(costPrice)
                    setattr(sale, 'totalCostPrice', totalCostPrice)
                    try:
                        grossProfit = sale.total_net - totalCostPrice
                        status = 'true'
                        margin = round((grossProfit / sale.total_net) * 100, 2)
                    except:
                        grossProfit = 0
                        margin = 0
                    setattr(sale, 'margin', margin)
                    sales.append(sale)

        elif gid:
            csales = Sales.objects.filter(created__icontains=gid)
            for sale in csales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                for i in SoldItem.objects.filter(sales=sale):
                    product = ProductVariant.objects.get(sku=i.sku)
                    try:
                        quantity = product.get_cost_price().gross
                    except:
                        quantity = product.get_cost_price()
                    costPrice.append(quantity)
                totalCostPrice = sum(costPrice)
                setattr(sale, 'totalCostPrice', totalCostPrice)
                try:
                    grossProfit = sale.total_net - totalCostPrice
                    status = 'true'
                    margin = round((grossProfit / sale.total_net) * 100, 2)
                except:
                    grossProfit = 0
                    margin = 0
                setattr(sale, 'margin', margin)
                sales.append(sale)
        else:
            try:
                last_sale = Sales.objects.latest('id')
                gid = DateFormat(last_sale.created).format('Y-m-d')
            except:
                gid = DateFormat(datetime.datetime.today()).format('Y-m-d')

            csales = Sales.objects.filter(created__icontains=gid)
            for sale in csales:
                quantity = SoldItem.objects.filter(sales=sale).aggregate(c=Count('sku'))
                setattr(sale, 'quantity', quantity['c'])
                for i in SoldItem.objects.filter(sales=sale):
                    product = ProductVariant.objects.get(sku=i.sku)
                    try:
                        quantity = product.get_cost_price().gross
                    except:
                        quantity = product.get_cost_price()
                    costPrice.append(quantity)
                totalCostPrice = sum(costPrice)
                setattr(sale, 'totalCostPrice', totalCostPrice)
                try:
                    grossProfit = sale.total_net - totalCostPrice
                    status = 'true'
                    margin = round((grossProfit / sale.total_net) * 100, 2)
                except:
                    grossProfit = 0
                    margin = 0
                setattr(sale, 'margin', margin)
                sales.append(sale)

        img = image64()
        data = {
            'today': date.today(),
            'sales': sales,
            'puller': request.user,
            'image': img,
            'gid': gid
        }
        pdf = render_to_pdf('dashboard/reports/sales_margin2/pdf/saleslist_pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')


## sales margin items
@staff_member_required
def sales_items_paginate(request):
    page = int(request.GET.get('page'))
    list_sz = request.GET.get('size')
    p2_sz = request.GET.get('psize')
    select_sz = request.GET.get('select_size')
    date = request.GET.get('gid')
    sales = Sales.objects.all().order_by('-id')
    today_formart = DateFormat(datetime.date.today())
    today = today_formart.format('Y-m-d')
    ts = Sales.objects.filter(created__icontains=today)
    tsum = ts.aggregate(Sum('total_net'))
    total_sales = Sales.objects.aggregate(Sum('total_net'))
    total_tax = Sales.objects.aggregate(Sum('total_tax'))

    try:
        last_sale = Sales.objects.latest('id')
        last_date_of_sales = DateFormat(last_sale.created).format('Y-m-d')
        all_sales = Sales.objects.filter(created__contains=last_date_of_sales)
        total_sales_amount = all_sales.aggregate(Sum('total_net'))
        items = SoldItem.objects.values('product_name', 'product_category', 'sku',
                                        'unit_cost') \
            .annotate(Count('sku')) \
            .annotate(Sum('total_cost')) \
            .annotate(Sum('unit_cost')) \
            .annotate(Sum('quantity')).order_by('product_name')
        total_items = []
        for t in items:
            product = ProductVariant.objects.get(sku=t['sku'])
            try:
                itemPrice = product.get_cost_price().gross
            except:
                itemPrice = product.get_cost_price()
            unitSalesCost = t['unit_cost']
            totalSalesCost = t['total_cost__sum']
            try:
                grossProfit = unitSalesCost - itemPrice
                unitMargin = round((grossProfit / unitSalesCost) * 100, 2)
                salesGrossProfit = totalSalesCost - (itemPrice * t['quantity__sum'])
                salesMargin = round((salesGrossProfit / totalSalesCost) * 100, 2)
            except:
                grossProfit = 0
                unitMargin = 0
                salesMargin = 0
            t['unitMargin'] = unitMargin
            t['salesMargin'] = salesMargin
            total_items.append(t)

        if list_sz:
            paginator = Paginator(total_items, int(list_sz))
            total_items = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/p2.html',
                                    {'items': total_items, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                     'total_sales': total_sales, 'total_tax': total_tax, 'tsum': tsum})
        else:
            paginator = Paginator(total_items, 10)
        if p2_sz:
            paginator = Paginator(total_items, int(p2_sz))
            total_items = paginator.page(page)
            return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/paginate.html',
                                    {'items': total_items})

        try:
            total_items = paginator.page(page)
        except PageNotAnInteger:
            total_items = paginator.page(1)
        except InvalidPage:
            total_items = paginator.page(1)
        except EmptyPage:
            total_items = paginator.page(paginator.num_pages)
        return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/paginate.html', {'items': total_items})
    except ObjectDoesNotExist as e:
        return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/p2.html', {'date': date})


@staff_member_required
def sales_items_search(request):
    if request.is_ajax():
        page = request.GET.get('page', 1)
        list_sz = request.GET.get('size')
        p2_sz = request.GET.get('psize')
        q = request.GET.get('q')
        if list_sz is None:
            sz = 10
        else:
            sz = list_sz

        if q is not None:
            allItems = SoldItem.objects.values('product_name', 'product_category', 'sku',
                                               'unit_cost') \
                .annotate(Count('sku')) \
                .annotate(Sum('total_cost')) \
                .annotate(Sum('unit_cost')) \
                .annotate(Sum('quantity')).order_by('product_name')
            all_items = allItems.filter(
                Q(sku__icontains=q) |
                Q(product_name__icontains=q) |
                Q(product_category__icontains=q))

            items = all_items
            total_items = []
            for t in items:
                product = ProductVariant.objects.get(sku=t['sku'])
                try:
                    itemPrice = product.get_cost_price().gross
                except:
                    itemPrice = product.get_cost_price()
                unitSalesCost = t['unit_cost']
                totalSalesCost = t['total_cost__sum']
                try:
                    grossProfit = unitSalesCost - itemPrice
                    unitMargin = round((grossProfit / unitSalesCost) * 100, 2)
                    salesGrossProfit = totalSalesCost - (itemPrice * t['quantity__sum'])
                    salesMargin = round((salesGrossProfit / totalSalesCost) * 100, 2)
                except:
                    grossProfit = 0
                    unitMargin = 0
                    salesMargin = 0
                t['unitMargin'] = unitMargin
                t['salesMargin'] = salesMargin
                total_items.append(t)
            if list_sz:
                paginator = Paginator(total_items, int(list_sz))
                total_items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/search.html',
                                        {'items': total_items, 'pn': paginator.num_pages, 'sz': list_sz, 'gid': 0,
                                         'q': q})

            if p2_sz:
                paginator = Paginator(total_items, int(p2_sz))
                total_items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/paginate.html',
                                        {'items': total_items})

            paginator = Paginator(total_items, 10)
            try:
                total_items = paginator.page(page)
            except PageNotAnInteger:
                total_items = paginator.page(1)
            except InvalidPage:
                total_items = paginator.page(1)
            except EmptyPage:
                total_items = paginator.page(paginator.num_pages)
            if p2_sz:
                total_items = paginator.page(page)
                return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/paginate.html',
                                        {'items': total_items})

            return TemplateResponse(request, 'dashboard/reports/sales_margin2/items/search.html',
                                    {'items': total_items, 'pn': paginator.num_pages, 'sz': sz, 'q': q})


@staff_member_required
def sales_list_margin_items_pdf(request):
    if request.is_ajax():
        q = request.GET.get('q')
        gid = request.GET.get('gid')

        if gid:
            gid = gid
        else:
            gid = None

        sales = []
        costPrice = []
        if q is not None:
            allItems = SoldItem.objects.values('product_name', 'product_category', 'sku',
                                               'unit_cost') \
                .annotate(Count('sku')) \
                .annotate(Sum('total_cost')) \
                .annotate(Sum('unit_cost')) \
                .annotate(Sum('quantity')).order_by('product_name')
            all_items = allItems.filter(
                Q(sku__icontains=q) |
                Q(product_name__icontains=q) |
                Q(product_category__icontains=q))

            items = all_items
            total_items = []
            for t in items:
                product = ProductVariant.objects.get(sku=t['sku'])
                try:
                    itemPrice = product.get_cost_price().gross
                except:
                    itemPrice = product.get_cost_price()
                unitSalesCost = t['unit_cost']
                totalSalesCost = t['total_cost__sum']
                try:
                    grossProfit = unitSalesCost - itemPrice
                    unitMargin = round((grossProfit / unitSalesCost) * 100, 2)
                    salesGrossProfit = totalSalesCost - (itemPrice * t['quantity__sum'])
                    salesMargin = round((salesGrossProfit / totalSalesCost) * 100, 2)
                except:
                    grossProfit = 0
                    unitMargin = 0
                    salesMargin = 0
                t['unitMargin'] = unitMargin
                t['salesMargin'] = salesMargin
                total_items.append(t)


        else:
            items = SoldItem.objects.values('product_name', 'product_category', 'sku',
                                            'unit_cost') \
                .annotate(Count('sku')) \
                .annotate(Sum('total_cost')) \
                .annotate(Sum('unit_cost')) \
                .annotate(Sum('quantity')).order_by('product_name')
            total_items = []
            for t in items:
                product = ProductVariant.objects.get(sku=t['sku'])
                try:
                    itemPrice = product.get_cost_price().gross
                except:
                    itemPrice = product.get_cost_price()
                unitSalesCost = t['unit_cost']
                totalSalesCost = t['total_cost__sum']
                try:
                    grossProfit = unitSalesCost - itemPrice
                    unitMargin = round((grossProfit / unitSalesCost) * 100, 2)
                    salesGrossProfit = totalSalesCost - (itemPrice * t['quantity__sum'])
                    salesMargin = round((salesGrossProfit / totalSalesCost) * 100, 2)
                except:
                    grossProfit = 0
                    unitMargin = 0
                    salesMargin = 0
                t['unitMargin'] = unitMargin
                t['salesMargin'] = salesMargin
                total_items.append(t)

        img = image64()
        data = {
            'today': date.today(),
            'items': total_items,
            'puller': request.user,
            'image': img,
            'gid': gid
        }
        pdf = render_to_pdf('dashboard/reports/sales_margin2/pdf/margin_items.html', data)
        return HttpResponse(pdf, content_type='application/pdf')
