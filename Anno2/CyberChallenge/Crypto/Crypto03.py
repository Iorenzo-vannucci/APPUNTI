from base64 import b64decode
FirstHalf = 'ZmxhZ3t3NDF0XzF0c19hbGxfYjE='
primo=b64decode(FirstHalf)

SecondHalf = 664813035583918006462745898431981286737635929725

secondo=(SecondHalf).to_bytes(20,'big')

tot = primo=primo+secondo
print(tot)

