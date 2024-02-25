def user_group(request):
  user_belong_to_store = request.user.groups.filter(name='store').exists()
  return {'user_belong_to_store': user_belong_to_store}