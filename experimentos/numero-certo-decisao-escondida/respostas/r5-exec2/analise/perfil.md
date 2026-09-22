# Perfil do arquivo

## Formato

- arquivo: BASE DE PACING_v2.csv.xls
- extensao: xls
- bytes: 3049125
- separador: ,
- quebra_linha: CRLF
- encoding: utf-8-sig
- bom: True
- formato_real: csv
- extensao_confere: False
- ATENCAO: a extensao .xls nao corresponde ao conteudo, que e csv

## Forma: 16809 linhas, 14 colunas, 0 duplicatas exatas

| coluna | tipo | nulos | nulos em texto | distintos | artefatos float | exemplos |
|---|---|---|---|---|---|---|
| Base | object | 0 | 0 | 2 | 0 | Planejado; Realizado |
| campaign_name | object | 45 | 0 | 2790 | 0 | Marcasfilial_filial_acaocashback-janeiro_alcance_2301; Marcasfilial_filial_acao- |
| Campanha | object | 0 | 0 | 185 | 0 | Cashback; Cashback Resgate; Especial Cabelos; Fds1; Fds2 |
| Soma de Cliques | int64 | 0 | 0 | 2259 | 0 | 12920; 4320; 1546; 809; 1872 |
| Data | object | 0 | 0 | 584 | 0 | 2024-05-28 00:00:00; 2024-07-01 00:00:00; 2024-06-10 00:00:00; 2024-07-08 00:00: |
| Data de Inicio | object | 16764 | 0 | 15 | 0 | 2024-05-28 00:00:00; 2024-07-01 00:00:00; 2024-06-10 00:00:00; 2024-07-08 00:00: |
| Data de Termino | object | 16764 | 0 | 11 | 0 | 2024-06-07 00:00:00; 2024-07-07 00:00:00; 2024-06-30 00:00:00; 2024-07-31 00:00: |
| Soma de Dias_Veiculacao | float64 | 16764 | 0 | 11 | 0 | 10.0; 6.0; 20.0; 23.0; 12.0 |
| Soma de Impressoes | int64 | 0 | 0 | 14783 | 0 | 6460000; 2160000; 257760; 135000; 1250000 |
| Soma de Investimento | float64 | 2 | 0 | 16670 | 38 | 64600.0; 41040.0; 19847.51953125; 7020.0; 5000.0 |
| Modalidade | object | 0 | 0 | 56 | 0 | Regular; Trade; Inauguracao; Acaocashback Janeiro; Acao Influenciadora Lais Cint |
| Objetivo | object | 0 | 18 | 7 | 0 | Alcance; Engajamento; Video Views; Trafego; Conversao |
| Publico | object | 0 | 241 | 3 | 0 | Socios; Nao Socios; N/a |
| Veiculo | object | 0 | 0 | 3 | 0 | Meta Ads; Youtube Ads; Tiktok Ads |

## Colunas nulas juntas

- campaign_name: nulas juntas em 45 linhas
  - explicado por `Base` = ['Planejado']. Provavel mistura de duas tabelas com grao diferente
- Data de Inicio, Data de Termino, Soma de Dias_Veiculacao: nulas juntas em 16764 linhas
  - explicado por `Base` = ['Realizado']. Provavel mistura de duas tabelas com grao diferente
- Soma de Investimento: nulas juntas em 2 linhas

## Variantes de categoria por prefixo

- Campanha: ['Casa Limpa', 'Casa Limpa 3m', 'Casa Limpa Organizada']
- Campanha: ['Cashback', 'Cashback Resgate']
- Campanha: ['Fds1', 'Fds1 Out', 'Fds1 Set']
- Campanha: ['Fds2', 'Fds2 Ofertasbr']
- Campanha: ['Fds3', 'Fds3 Ofertasbr']
- Campanha: ['Fds4', 'Fds4 Ofertasbr']
- Campanha: ['Fds5', 'Fds5 Ofertasbr']
- Campanha: ['Freeshop', 'Freeshop From Like To Love', 'Freeshop Gui', 'Freeshop Jesk', 'Freeshop Time To Try', 'Freeshop Vini']
- Campanha: ['Inauguracao', 'Inauguracao Barra', 'Inauguracao Bonoco', 'Inauguracao Cristal', 'Inauguracao Florianopolis', 'Inauguracao Lauro']
- Campanha: ['Joao Pessoa', 'Joao Pessoa - Não Pulavel']
- Campanha: ['Material Didatico', 'Material Didatico Emb Economicas Novidades', 'Material Didatico Influ', 'Material Didatico Parceiros Cashback', 'Material Didatico Queridinhos So Tem No Marcas']
- Campanha: ['Natal', 'Natal Angola', 'Natal Japao', 'Natal Previa', 'Natal Ucrania']
- Campanha: ['Novidades', 'Novidades Marcas']
- Campanha: ['Pascoa', 'Pascoa Aquecimento', 'Pascoa Lancamento', 'Pascoa Sustentacao']
- Modalidade: ['Regular', 'Regular Janeiro Fds1 Cone', 'Regular Janeiro Fds1 Cone Nsocio Interesses', 'Regular Janeiro Fds1 Cone Nsocio Lookalike', 'Regular Janeiro Fds1 Nsocio', 'Regular Janeiro Fds1 Sp', 'Regular Janeiro Fds1 Sp Nsocio Interesses', 'Regular Janeiro Fds1 Sp Nsocio Lookalike', 'Regular Janeiro Fds1 Sulsudeste', 'Regular Janeiro Fds1 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds1 Sulsudeste Nsocio Lookalike', 'Regular Janeiro Fds2 Cone', 'Regular Janeiro Fds2 Cone Nsocio Interesses', 'Regular Janeiro Fds2 Cone Nsocio Lookalike', 'Regular Janeiro Fds2 Sp', 'Regular Janeiro Fds2 Sp Nsocio Interesses', 'Regular Janeiro Fds2 Sp Nsocio Lookalike', 'Regular Janeiro Fds2 Sulsudeste', 'Regular Janeiro Fds2 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds2 Sulsudeste Nsocio Lookalike', 'Regular Janeiro Fds3 Cone', 'Regular Janeiro Fds3 Cone Nsocio Interesses', 'Regular Janeiro Fds3 Cone Nsocio Lookalike', 'Regular Janeiro Fds3 Sp', 'Regular Janeiro Fds3 Sp Nsocio Interesses', 'Regular Janeiro Fds3 Sp Nsocio Lookalike', 'Regular Janeiro Fds3 Sulsudeste', 'Regular Janeiro Fds3 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds3 Sulsudeste Nsocio Lookalike', 'Regular Janeiro Fds4 Cone', 'Regular Janeiro Fds4 Cone Nsocio Interesses', 'Regular Janeiro Fds4 Cone Nsocio Lookalike', 'Regular Janeiro Fds4 Sp', 'Regular Janeiro Fds4 Sp Nsocio Interesses', 'Regular Janeiro Fds4 Sp Nsocio Lookalike', 'Regular Janeiro Fds4 Sulsudeste', 'Regular Janeiro Fds4 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds4 Sulsudeste Nsocio Lookalike', 'Regular Janeiro Happy Hour', 'Regular Janeiro Megaday Nsocios', 'Regular Janeiro Megaday Socios', 'Regular Janeiro Solucao Da Casa']
- Modalidade: ['Regular Janeiro Fds1 Cone', 'Regular Janeiro Fds1 Cone Nsocio Interesses', 'Regular Janeiro Fds1 Cone Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds1 Sp', 'Regular Janeiro Fds1 Sp Nsocio Interesses', 'Regular Janeiro Fds1 Sp Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds1 Sulsudeste', 'Regular Janeiro Fds1 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds1 Sulsudeste Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds2 Cone', 'Regular Janeiro Fds2 Cone Nsocio Interesses', 'Regular Janeiro Fds2 Cone Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds2 Sp', 'Regular Janeiro Fds2 Sp Nsocio Interesses', 'Regular Janeiro Fds2 Sp Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds2 Sulsudeste', 'Regular Janeiro Fds2 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds2 Sulsudeste Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds3 Cone', 'Regular Janeiro Fds3 Cone Nsocio Interesses', 'Regular Janeiro Fds3 Cone Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds3 Sp', 'Regular Janeiro Fds3 Sp Nsocio Interesses', 'Regular Janeiro Fds3 Sp Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds3 Sulsudeste', 'Regular Janeiro Fds3 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds3 Sulsudeste Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds4 Cone', 'Regular Janeiro Fds4 Cone Nsocio Interesses', 'Regular Janeiro Fds4 Cone Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds4 Sp', 'Regular Janeiro Fds4 Sp Nsocio Interesses', 'Regular Janeiro Fds4 Sp Nsocio Lookalike']
- Modalidade: ['Regular Janeiro Fds4 Sulsudeste', 'Regular Janeiro Fds4 Sulsudeste Nsocio Interesses', 'Regular Janeiro Fds4 Sulsudeste Nsocio Lookalike']
- Modalidade: ['Trade', 'Trade Lg Week']
