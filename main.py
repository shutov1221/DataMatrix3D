import ServerConnection


def main_loop(replacer):
    active = True
    while active:
        print('Введите название кейса')
        case = input().upper()
        status = replacer.replace_file(case)
        if not status:
            active = True
        else:
            active = False


if __name__ == '__main__':
    connection_settings = ServerConnection.read_connection_settings()

    connect_to_sm = ServerConnection.SSConnection(connection_settings[0],
                                                  connection_settings[1],
                                                  connection_settings[2],
                                                  connection_settings[3],
                                                  connection_settings[4])

    connection = connect_to_sm.connect()

    ss_repos = ServerConnection.SSRepository(connection, '3DS', 'project')

    ss_replacer = ServerConnection.SSReplacer(ss_repos, 'C:\\Users\\User\\AppData\\Roaming\\Replacer')

    main_loop(ss_replacer)

