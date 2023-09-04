async def update_without_renew() -> str:
    return """UPDATE public.user_subscribes
              SET active = False
              WHERE public.user_subscribes.id in
              (SELECT public.user_subscribes.id AS subscribe_id
              FROM public.user_subscribes
              JOIN public.orders ON public.user_subscribes.order_id = public.orders.id
              JOIN public.type_subscribes ON public.user_subscribes.type_subscribe_id = public.type_subscribes.id
              WHERE public.orders.renew = False
              AND public.user_subscribes.active = True                
              AND 
              CASE WHEN period = '1mon'
              THEN (public.user_subscribes.start_active_at + '1mon'::INTERVAL) < CURRENT_DATE
              WHEN period = '3mon'
              THEN (public.user_subscribes.start_active_at + '3mon'::INTERVAL) < CURRENT_DATE
              WHEN period = '6mon'
              THEN (public.user_subscribes.start_active_at + '6mon'::INTERVAL) < CURRENT_DATE
              WHEN period = '12mon'
              THEN (public.user_subscribes.start_active_at + '12mon'::INTERVAL) < CURRENT_DATE
              END)
              RETURNING public.user_subscribes.id"""


async def get_renew_subscriptions() -> str:
    return """SELECT public.user_subscribes.id AS subscribe_id,
              payment_id,
              public.user_subscribes.user_id AS user_id,
              price
              FROM public.user_subscribes
              JOIN public.orders ON public.user_subscribes.order_id = public.orders.id
              JOIN public.type_subscribes ON public.user_subscribes.type_subscribe_id = public.type_subscribes.id
              WHERE public.orders.renew = True
              AND public.user_subscribes.active = True                
              AND 
              CASE WHEN period = '1mon'
              THEN (public.user_subscribes.start_active_at + '1mon'::INTERVAL) < CURRENT_DATE
              WHEN period = '3mon'
              THEN (public.user_subscribes.start_active_at + '3mon'::INTERVAL) < CURRENT_DATE
              WHEN period = '6mon'
              THEN (public.user_subscribes.start_active_at + '6mon'::INTERVAL) < CURRENT_DATE
              WHEN period = '12mon'
              THEN (public.user_subscribes.start_active_at + '12mon'::INTERVAL) < CURRENT_DATE
              END"""
