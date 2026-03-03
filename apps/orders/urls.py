from django.urls import path

from .views import (
    KitchenBoardView,
    KitchenMarkItemReadyView,
    OrderAddItemView,
    OrderCreateView,
    OrderDetailView,
    OrderListView,
    OrderMarkCompletedView,
    OrderRemoveItemView,
    OrderSendToKitchenView,
    OrderUpdateItemQtyView,
)


app_name = "orders"

urlpatterns = [
    path("", OrderListView.as_view(), name="order_list"),
    path("new/", OrderCreateView.as_view(), name="order_create"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("<int:pk>/add-item/", OrderAddItemView.as_view(), name="order_add_item"),
    path("<int:pk>/items/<int:item_pk>/set-qty/", OrderUpdateItemQtyView.as_view(), name="order_item_set_qty"),
    path("<int:pk>/items/<int:item_pk>/remove/", OrderRemoveItemView.as_view(), name="order_item_remove"),
    path("<int:pk>/send-to-kitchen/", OrderSendToKitchenView.as_view(), name="order_send_to_kitchen"),
    path("<int:pk>/mark-completed/", OrderMarkCompletedView.as_view(), name="order_mark_completed"),

    path("kitchen/", KitchenBoardView.as_view(), name="kitchen_board"),
    path("kitchen/<int:pk>/items/<int:item_pk>/ready/", KitchenMarkItemReadyView.as_view(), name="kitchen_item_ready"),
]

