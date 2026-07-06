import re 
x=re.findall("/^flag\{[\D]{2}[0][a-z][^0-9][L][\w]{4}[^a-pr-z]{3}[^\d]{2}[\d][b]\}$/",)
print(x)