faturamento = 1000
custo = 700

novas_vendas = 300

faturamento = faturamento + novas_vendas #somar
imposto = faturamento * 0.1 #multiplicar
lucro = faturamento - custo - imposto #subtrair

print(faturamento)
print(lucro)

margem_lucro = lucro / faturamento #dividir
print(margem_lucro)

restituicao = imposto * 0.1
print(restituicao)

#restituicao= faturamento ** 0.1 #a potência
#print(restituicao)

#mod resto da divisão
#10 % 3
tempo_em_meses = 160
tempo_em_anos = int(tempo_em_meses /12)
print(tempo_em_anos, "anos")
print(tempo_em_meses % 12, "meses")

numero = 112.57
print(round(numero)) #arredondamento

faturamento = 1_234_987_74 #anderline e uma edicição visual
