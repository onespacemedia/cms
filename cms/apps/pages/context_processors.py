"""Context processors used by the pages application."""
from geoip_utils import core as geoip


def pages(request):
    """Adds the current page backend to the template."""
    context = {
        "pages": request.pages,
        "geoip_data": geoip.get_country(request),
    }
    return context
