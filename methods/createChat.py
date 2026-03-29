def createChat(vk_session, title, group_id):
    answer = []
    answer.append(vk_session.method("messages.createChat", {"title": title, "group_id": group_id}))
    answer.append(vk_session.method("messages.getInviteLink", {"peer_id": 2000000000 + answer[0], "group_id": group_id}))
    return answer