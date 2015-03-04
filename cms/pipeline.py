def make_staff(backend, user, response, *args, **kwargs):
    if backend.name == 'google-plus':
        user.is_staff = True
        user.is_superuser = True
        user.save()
