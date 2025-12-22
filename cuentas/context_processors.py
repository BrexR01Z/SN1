def invitaciones_pendientes(request):
    """
    Context processor que agrega invitaciones pendientes a TODAS las páginas
    """
    if request.user.is_authenticated:
        invitacion_pendiente = request.user.received_invitations.filter(
            accepted=False
        ).order_by('-created_at').first()
        
        return {
            'invitacion_pendiente': invitacion_pendiente
        }
    
    return {
        'invitacion_pendiente': None
    }