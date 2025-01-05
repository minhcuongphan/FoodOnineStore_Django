def detectUser(user):
    if user.role == 1:
        redirectUrl = 'vendorDashboard'
    if user.role == 2:
        redirectUrl = 'custDashboard'
    if user.role == None and user.is_superadmin:
        redirectUrl = '/admin'

    return redirectUrl