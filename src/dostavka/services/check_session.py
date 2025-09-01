
async def check_session(session_id: str, package_dal, session_dal):
    existing_session = await session_dal.get_session_by_id(session_id)
    if not existing_session:
        await session_dal.create_session(session_id)
        existing_session = await session_dal.get_session_by_id(session_id)
    await session_dal.update_last_activity(session_id)
