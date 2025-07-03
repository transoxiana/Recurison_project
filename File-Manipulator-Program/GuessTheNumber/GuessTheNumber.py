import random

print('Welcome to Guess the Number Game\n'
      + 'How to play:\n'
      + '1.Enter two integers, m and n(The differences between m and n should be at least 3.)\n'
      + '2.A random integer between m and n (inclusive) will be selected.Try to guess the selected number\n'
      + '3.You have up to 3 attempts to guess the number')
m = input('What is m number?\n')
if(not m.isdigit()):
    print('Enter integers!')
    exit()
n = input ('What is n number?\n')
if(not n.isdigit()):
    print('Enter integers!')
    exit()
m1 = int(m)
n1 = int(n)
if(m1 < n1):
    temp = m1
    m1 = n1
    n1 = temp
if(m1 - n1 <3):
    print('The differences between m and n should be at least 3!')
    exit()
target_number = random.randint(n1,m1)
for i in range(3):
    responce_number = input('What is your ansewer number?\n')
    if str(target_number) == responce_number:
        print('That`s right!!')
        exit()
    print('Try again!')

print('Nice try!')