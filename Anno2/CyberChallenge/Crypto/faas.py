import sys
import requests as r


class Faas:

    def __init__(self, hostname, app_id, wait_token=None, refresh_token=None, debug=False):
        self.app_id = app_id
        self.refresh_token = refresh_token
        self.wait_token = wait_token
        self.base_url = f'http://{hostname}/api'
        self.debug = debug

        # ask the the api for the auth

    def authorize(self):
        """
            Asks the authorization to the owner of the app
            Returns a "wait_token", that can be used to check whether the user has given an authorization
            and to retrive the auth token
        """
        url = self.base_url + '/authorize/{}'.format(self.app_id)
        if self.debug:
            print(url)

        resp = r.get(url).json()

        self.wait_token = resp['token']
        if self.debug:
            print(f"Status: {resp['token']}")
        return resp['token']

    def get_refresh_token(self):
        """
            Check if the user has given the authorization.
            If so returns an refresh token, that can be used to retrieve an authtoken.
            Note that once the refresh token is retrieve, the "wait_token" is not valid anymore
        """

        url = self.base_url + '/get_refresh/{}'.format(self.wait_token)

        if self.debug:
            print(url)

        resp = r.get(url).json()
        if 'status' in resp and  resp['status'] == 'accepted':
            self.refresh_token = resp['token']
            return resp['token']
        else:
            if self.debug:
                print(f"Status: {resp['status']}")
            return False

    def get_auth_token(self):
        """
            Retrieves an auth token that can be used to query the app
        """

        url  = self.base_url + '/refresh/{}'.format(self.refresh_token)
        if self.debug:
            print(url)

        resp = r.get(url)
        
        if resp.status_code == 401:
            if self.debug:
                print("Invalid refresh token")
            return False

        resp = resp.json()

        self.auth_token = resp['token']
        if self.debug:
            print(resp['token'])
        return resp['token']

    def set(self, key, value):
        """
        Sets a key to a value
        """
        url = self.base_url + '/set/{}/{}'.format(self.app_id, key)
        if self.debug:
            print(url)
        headers = {'Auth': self.auth_token}
        data = {'value': value}
        resp = r.post(url,
                      headers=headers, json=data)
       
        if resp.status_code == 401:
            print('Invalid auth_token. Check your refresh token')
            return 'Invalid auth_token. Check your refresh token'
        return resp.json()['status']

    def get(self, key):
        """
        Gets the value of a key
        """
        url = self.base_url+ '/get/{}/{}'.format(self.app_id, key)

        headers = {'Auth': self.auth_token}
        if self.debug:
            print(url)

        resp = r.get(url, headers=headers)
        print(f"ATTENZIONE QUESTO è IL JWT:{resp.json()['token']}")
        if resp.status_code == 401:
            print('Invalid auth_token. Check your refresh token')
            return 
        return resp.json()['data']


if __name__ == '__main__':
    HELP_TEXT = f'''Usage: {sys.argv[0]} <hostname> <app_id> [command] [command_args] [wait_token|refresh_token]
[command] can be:
    get             : Retrives a value from the app. Needs a key and a refresh token
    set             : Sets a value in the store. Needs a key, a value and a refresh token
    check_auth      : Checks the authorization status. Needs a wait token
    ask_auth        : Asks the owner of the app for an authorization. Doesn't require any token

Examples:
{sys.argv[0]} foobar.com <app_id> get flag <refresh_token>  : Retrieves the "flag" from an app using the provided refresh token
{sys.argv[0]} foobar.com <app_id> check_auth <wait_token>   : Check whether the user has given us permission to use the app
{sys.argv[0]} foobar.com <app_id> ask_auth                  : Ask the owner of <app_id> the authorization for accessing the data stored in the app
'''
    if 'help' in sys.argv or len(sys.argv) < 4:
        print(HELP_TEXT)
        quit()
        
    if sys.argv[3] not in ['get', 'set', 'check_auth', 'ask_auth']:
        print(HELP_TEXT)
        quit()

    hostname = sys.argv[1]
    app_id = sys.argv[2]
    command = sys.argv[3]

    if command == 'ask_auth':
        faas = Faas(hostname, app_id)
        print('Ok.')
        wait_token = faas.authorize()
        print(f'wait token: {wait_token}')
        quit()
    
    if command == 'check_auth' and len(sys.argv) < 5:
        print(HELP_TEXT)
        quit()
    
    if command == 'check_auth':
        wait_token = sys.argv[4]
        print('Ok.')
        faas = Faas(hostname, app_id, wait_token=wait_token)
        resp = faas.get_refresh_token()

        if resp:
            print(f"Auth token: {resp}")
            print(f"Remember to save it somewhere, the wait token is now expired")
            quit()
        else:
            print('No auth for the moment. Try later')
            quit()
    
    if command == 'get' and len(sys.argv) < 6:
        print(HELP_TEXT)
        quit()
    
    if command == 'get':
        refresh_token = sys.argv[5]
        key = sys.argv[4]
        print('Ok.')
        faas = Faas(hostname, app_id, refresh_token=refresh_token)
        if not faas.get_auth_token():
            print("Invalid refresh token")
            quit()
        resp = faas.get(key)
        print(f'resp: {resp}')
    
    if command == 'set' and len(sys.argv) < 7:
        print(HELP_TEXT)
        quit()
    
    if command == 'set':
        key = sys.argv[4]
        value = sys.argv[5]
        refresh_token = sys.argv[6]

        print('Ok.')
        faas = Faas(hostname, app_id, refresh_token=refresh_token)
        if not faas.get_auth_token():
            print("Invalid refresh token")
            quit()
        resp = faas.set(key, value)
        print(f'resp: {resp}')
        