import random

GREMLIN_ERROR_MESSAGES = [
    "Oops! It looks like the gremlins are at it again! We're on the chase and should have things back to normal soon.",
    "Our server gremlins are causing mischief! We're currently trying to negotiate with them. Please hold tight!",
    "We've detected some gremlin shenanigans in our server room! Hang tight while we sort out their mess.",
    "Seems our gremlins got overly excited and messed something up. We're working on a peace treaty now. Check back shortly!",
    "Alert: Gremlins have invaded our server! We’re deploying anti-gremlin measures. Your patience is magical!",
    "Gremlin alert! These little troublemakers have tinkered with our servers. Restoration spells in progress.",
    "Our gremlins are having a party in the server room. We've asked them to turn down the music and fix the servers ASAP!",
    "Whoops! Gremlins stole our server cables. We're negotiating their return; please stay tuned!",
    "Server gremlins have struck again! We're sending in the gremlin busters. Service will resume shortly.",
    "Gremlins on the loose! They’re causing havoc, but we’re on a mission to bring peace back to our servers."
]


def get_random_gremlin_error_message():
    return random.choice(GREMLIN_ERROR_MESSAGES)
