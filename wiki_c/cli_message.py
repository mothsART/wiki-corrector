from colored import fg, bg, attr


def success_message(message):
    print (
        '%s%s %s %s' % (
            fg('white'), bg('green'), message, attr('reset')
        )
    )

def error_message(message):
    print (
        '%s%s %s %s' % (
            fg('white'), bg('red'), message, attr('reset')
        )
    )
