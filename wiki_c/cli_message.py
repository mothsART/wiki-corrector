from colored import fg, bg, attr


def success_message(message):
    print (
        '%s%s %s %s' % (
            fg('white'), bg('green'), message, attr('reset')
        )
    )

def warning_message(message):
    print (
        '%s%s %s %s' % (
            fg('white'), bg('dark_orange_3a'), message, attr('reset')
        )
    )

def error_message(message):
    print (
        '%s%s %s %s' % (
            fg('white'), bg('red'), message, attr('reset')
        )
    )
