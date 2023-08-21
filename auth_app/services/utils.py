from user_agents import parse


def get_device_type(user_agent_info: str) -> str:

    user_agent = parse(user_agent_info)
    if user_agent.is_mobile:
        return 'mobile'
    elif user_agent.is_pc:
        return 'web'
    elif user_agent.is_tablet:
        return 'tablet'
    else:
        return 'web'
