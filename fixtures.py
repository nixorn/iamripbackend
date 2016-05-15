sources = [{'name': 'vk'},
           {'name': 'twitter'},
           {'name': 'facebook'}]

users = [{'username': 'iamrip',
          'email': 'iamrip',
          'token': 'iamrip',
          'password': 'iamrip',
          'firstname': 'iamrip',
          'lastname': 'iamrip',}]

messages = [{'user_id': 1,
             'text': 'so, guys. I am rip.'}]


timers = [{'duration': 10000,
           'message_id': 1}]

source_records = [{'user_id': 1,
                   'source_id': 1}]

fixtures = {'Source': sources,
            'SourceRecord': source_records,
            'User': users,
            'Message': messages,
            'Timer': timers}
