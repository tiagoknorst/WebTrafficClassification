# -*- coding: utf-8 -*-
"""Aula02_Árvores de Decisão.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uzX18VpA_AeMdOnxl_uvxMfZbjIW0gFO

# CMP263 - Aprendizagem de Máquina - INF/UFRGS

## Atividade Prática: Árvores de Decisão

As árvores de decisão são conhecidas por possuírem um baixo viés, ao mesmo tempo em que apresentam alta variância.
Isto é, o método é capaz de modelar fronteiras de decisão bastante complexas, o que, por um lado, é positivo, mas torna o algoritmo bastante suscetível a ruído ou a padrões nos dados de treino que não generalizam para instâncias de teste.
Por isso, técnicas de poda são fundamentais para o uso efetivo do modelo em dados novos.

Nessa atividade, iremos analisar como a estrutura e as predições da árvore de decisão são afetadas por pequenas variações no conjunto de treino. Além disso, veremos duas técnicas de poda que podem ser usadas para controlar a complexidade do modelo.

**Este *colab* deve ser usado como base para o preenchimento do questionário encontrado no Moodle. Faça uma cópia do mesmo para realizar o exercício.** A forma mais fácil para duplicar este *colab* é ir em File > "Save a Copy in Drive". Não é necessário entregar este *colab* preenchido, mas guarde-o para caso ache que algum questionário está errado.

### Objetivos da Atividade
* Analisar os impactos da característica de **variância** nas árvores de decisão.
* Analisar o efeito da **poda** em árvores de decisão.

## Carregamento dos Dados

Além de possuir uma grande quantidade de algoritmos de aprendizado de máquina, a biblioteca [scikit-learn](https://scikit-learn.org/stable/index.html) possui também funções para carregar alguns conjuntos de dados.

Nessa seção, vamos usar essas funções para carregar o dataset [Breast Cancer Winconsin](https://scikit-learn.org/stable/datasets/toy_dataset.html#breast-cancer-dataset). Esse dataset possui um total de 30 atributos relativos a características de tumores de mama e um atributo alvo binário, que indica se o tumor é maligno ou benigno. Todos os 30 atributos são valores reais.

### Obtenção e análise dos dados
O código abaixo carrega o dataset utilizando as funções do scikit-learn e mostra algumas informações básicas sobre os dados
"""

import pandas as pd             # biblioteca para análise de dados
import matplotlib.pyplot as plt # biblioteca para visualização de informações
import seaborn as sns           # biblioteca para visualização de informações
import numpy as np              # biblioteca para operações com arrays multidimensionais
import ipaddress                # biblioteca para converter string IP para inteiro
import glob                     # biblioteca para acessar arquivos facilmente
from sklearn.neighbors import KNeighborsClassifier # biblioteca para treinar KNN
sns.set()

file="ISCXTor2016_TOR-NonTOR.csv"
data = pd.read_csv(file, dtype={'Source IP':str,
                                'Source Port':int,
                                'Destination IP':str,
                                'Destination Port':int,
                                'Protocol':int,
                                'Flow Duration':int,
                                'Flow Bytes/s':float,
                                'Flow Packets/s':float,
                                'Flow IAT Mean':float,
                                'Flow IAT Std':float,
                                'Flow IAT Max':float,
                                'Flow IAT Min':float,
                                'Fwd IAT Mean':float,
                                'Fwd IAT Std':float,
                                'Fwd IAT Max':float,
                                'Fwd IAT Min':float,
                                'Bwd IAT Mean':float, 
                                'Bwd IAT Std':float,
                                'Bwd IAT Max':float,
                                'Bwd IAT Min':float,
                                'Active Mean':int, 
                                'Active Std':int, 
                                'Active Max':int, 
                                'Active Min':int,
                                'Idle Mean':int, 
                                'Idle Std':int, 
                                'Idle Max':int, 
                                'Idle Min':int,
                                'label':str},)



#data = data.drop(columns=['Address A', 'Address B'])

## Características gerais do dataset
print("O conjunto de dados completo possui {} linhas e {} colunas".format(data.shape[0], data.shape[1]))


data.columns = data.columns.str.replace(' ', '') # elimina espaçamentos nos nomes dos atributos

print(data.head())
print(data.tail())

#data.AddressA=int(ipaddress.ip_address(data.AddressA))
for i in (range(data.shape[0])):
    data.at[i, 'SourceIP'] = int(ipaddress.ip_address(data.at[i, 'SourceIP'])) # converte IP para inteiro
    data.at[i, 'DestinationIP'] = int(ipaddress.ip_address(data.at[i, 'DestinationIP'])) # converte IP para inteiro



"""A coluna *'diagnosis'* contém a classificação de cada amostra referente ao tipo de tumor, se maligno (M) ou benigno (B). Vamos avaliar como as instâncias estão distribuídas entre as classes presentes no dataset."""

## Distribuição do atributo alvo, 'diagnosis'
#plt.hist(data['Malware'])
#plt.title("Distribuição do atributo alvo - Malware")
#plt.show()

"""Podemos perceber que existem mais instâncias classificadas como 'Benigno' do que como 'Maligno'. Portanto, existe um certo **desbalanceamento entre as classes**. Não vamos entrar em detalhes nesta atividade do possível impacto deste desbalanceamento no desempenho do modelo e tampouco como mitigar seus efeitos. Discutiremos esse assunto mais adiante. Por enquanto, é importante sabermos que temos mais exemplos do tipo 'Benigno' nos dados de treinamento, e portanto, é provável que qualquer modelo treinado tenha mais facilidade de acertar exemplos desta classe.

Vamos avaliar a distribuição de valores dos atributos preditivos. Faremos isto tanto através da sumarização da distribuição a partir do método `describe()`, como através da visualização dos histogramas para cada atributo utilizando o método `hist()`.
"""

#data.drop(['Malware'],axis=1).describe()

#data.drop(['Malware'],axis=1).hist(bins=15, figsize=(20,18))
#plt.show()


#plt.figure(figsize=(15,15))
#sns.heatmap(data.corr(), annot=True, cmap="PuOr", annot_kws={"size": 9})
#plt.show()

"""---


### Criando conjuntos de treino e teste para avaliação de modelos

Um dos princípios mais importantes no desenvolvimento de modelos de Aprendizado de Máquina é nunca avaliar um modelo com os mesmos dados nos quais ele foi treinado. Se cometermos este erro, teremos uma avaliação muito otimista, pois o modelo pode simplesmente decorar todos os dados analisados durante o treinamento e demonstrar excelente desempenho preditivo para estes dados - o que não necessariamente se repetirá ao ser aplicado a novos dados. Assim, a validação de modelos deve ser sempre feita com dados independentes.

Em muitos casos, não temos um conjunto de treino e teste já definidos. Ou seja, recebemos um único conjunto de dados para o desenvolvimento do modelo. Desta forma, o método **Holdout** é uma estratégia simples e flexível para gerar conjuntos de dados independentes: um conjunto é usado para treinar o modelo e o outro para testar o modelo. É imprescindível que estes conjuntos de dados sejam disjuntos, isto é, não podem ter nenhuma instância em comum.

Algumas proporções para a divisão dos dados em treino/teste são comumente adotadas na literatura, por exemplo, 80%/20% e 75%/25%.

Para o Holdout, iremos utilizar o método `train_test_split()` da biblioteca [scikit-learn](https://scikit-learn.org/stable/), uma das bibliotecas de Aprendizado de Máquina mais conhecidas e utilizadas do Python. Leia a documentação do método [aqui](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html). O parâmetro *stratify* define que a divisão será feita seguindo a proporção de exemplos por classe determinada no vetor $y$ (rótulos).
"""

## Separa o dataset em duas variáveis: os atributos/entradas (X) e a classe/saída (y)
X = data.iloc[:, :-1].values  # matriz contendo os atributos
y = data.iloc[:, data.shape[1]-1].values  # vetor contendo a classe (0 para maligno e 1 para benigno) de cada instância
y = np.array([0 if y=='nonTOR' else 1 for y in y]) 
feature_names = data.columns.tolist() #data.feature_names  # nome de cada atributo
target_names = ["0.0", "1.0"]  # nome de cada classe


print(f"Dimensões de X: {X.shape}\n")
print(f"Dimensões de y: {y.shape}\n")
print(f"Nomes dos atributos: {feature_names}\n")
print(f"Nomes das classes: {target_names}")

"""Como pode ser visto, o dataset possui 569 exemplos, sendo cada exemplo constituído por 30 diferentes atributos.

### Quantidade de Exemplos de cada Classe
É possível também contar quantos exemplos pertencem à classe dos tumores malignos e quantos à classe dos benignos
"""

import numpy as np

n_malign = np.sum(y == 0)
n_benign = np.sum(y == 1)

print("Número de exemplos malignos: %d" % n_malign)
print("Número de exemplos benignos: %d" % n_benign)

"""## Variância nas Árvores de Decisão

### Analisando a Estrutura das Árvores

Como estudado em aula, a árvore de decisão é conhecida por ser um classificador com alta variância. Isso possui consequências na estrutura das árvores treinadas.

O código abaixo treina várias árvores de decisão com diferentes conjuntos de treino obtidos através do método holdout.
Use-o para responder à Questão 1 do questionário.
"""

from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split  # função do scikit-learn que implementa um holdout


def get_root_node(dt, feature_names):
    feature_idx = dt.tree_.feature[0]
    return feature_names[feature_idx]


n_repeats = 20
root_nodes = []

# variando o seed do holdout, geramos conjuntos de treino e teste um pouco diferentes a cada iteração
for split_random_state in range(0, n_repeats):
  # Holdout com 20% de dados de teste
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=split_random_state)

  # Treinamento da árvore usando os dados de treino
  dt = DecisionTreeClassifier(random_state=0)
  dt.fit(X_train, y_train)

  # Obtemos o atributo usado na raiz e o salvamos na lista
  root_node = get_root_node(dt, feature_names)
  root_nodes.append(root_node)

root_nodes

"""### Análise da Variação na Acurácia

A propriedade de variância também implica em efeitos na variabilidade do desempenho dos modelos. Para fins de exemplo, podemos usar a acurácia como medida de desempenho através das funções do scikit-learn. Entretanto, outras métricas de desempenho como Recall e Precisão, que são mais indicadas para problemas em que o número de instâncias por classe é desbalanceado (como é o caso deste conjunto de dados) poderiam também ser exploradas (a critério do aluno, podem ser adicionadas para observação, mas a questão deve ser respondida com base na acurácia).
"""

from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

dt = DecisionTreeClassifier()
dt.fit(X_train, y_train)
y_pred = dt.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Acurácia nos dados de teste: %.3f" % accuracy)

"""O código abaixo executa repetidas vezes o treinamento das árvores de decisão, da mesma forma que no item *Analisando a Estrutura das Árvores*.
Modifique-o de forma a obter a acurácia para cada execução e então calcule a média, desvio padrão, máximo e mínimo dos valores. Use esses resultados para responder à **Questão 2**.

**Atenção: Não mude os valores que estão sendo passados para os parâmetros random_state para garantir a reprodutibilidade do código**.

"""

from sklearn.metrics import recall_score

n_repeats = 20
accuracies = []

# variando o seed do holdout, geramos conjuntos de treino e teste um pouco diferentes a cada iteração
for split_random_state in range(0, n_repeats):
  # Holdout com 20% de dados de teste
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=split_random_state)

  # Nova instância da árvore de decisão
  dt = DecisionTreeClassifier(random_state=0)

  # Treine a árvore de decisão usando os dados de treino
  # ...
  dt.fit(X_train, y_train)

  # Calcule a acurácia nos dados de teste
  # ...
  y_pred = dt.predict(X_test)
  accuracy = accuracy_score(y_test, y_pred)
  recall = recall_score(y_test, y_pred)
  print("Acurácia/Recall nos dados de teste: %.3f %.3f" % (accuracy,recall))

  accuracies.append(accuracy)

# Calcule a média, desvio padrão, máximo e mínimo das acurácias (pode usar numpy)
# ...
print("Média %.3f" % np.mean(accuracies))
print("Desvio padrão %.3f" % np.std(accuracies))
print("Máximo %.3f" % np.max(accuracies))
print("Mínimo %.3f" % np.min(accuracies))

"""### Análise de Instância individuais

1. Treine novamente uma árvore de decisão usando um novo conjunto de treino gerado com a função train_test_split. Utilize 20% de dados de teste e, desta vez, não **especifique valor nenhum para o random_state**.

2. Faça a predição para as instâncias especificadas abaixo e preencha na tabela do excel indicada no **Moodle** a classificação encontrada (0 para maligno e 1 para benigno).

"""

X_interesting = X[[40, 86, 297, 135, 73], :]
Y_interesting = y[[40, 86, 297, 135, 73]]

#print("X_interesting")
#print(X_interesting)
#print("Y_interesting")
#print(Y_interesting)

# 1. Instancie uma nova árvore de decisão, dessa vez sem especificar o valor de random_state
dt = DecisionTreeClassifier()

# 2. Separe o conjunto em treino e teste, dessa vez sem especificar o valor de random_state
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 3. Treine a nova árvore usando o conjunto de treino
dt.fit(X_train, y_train)

# 4. Use a nova árvore treinada para obter predições para os valores de X_interesting acima.
y_pred = dt.predict(X_interesting)
print(y_pred)
accuracy = accuracy_score(Y_interesting, y_pred)
print("Acurácia nos dados de teste: %.3f" % accuracy)

"""## O Efeito da Poda

As árvores de decisão treinadas nos itens anteriores não possuíam nenhuma forma de poda. No entanto, é possível utilizar técnicas de poda através do scikit-learn. Como consequência, elas podem ter uma complexidade além do que é necessário na modelagem do problema.

### Exemplo de Pré-poda: profundidade máxima da árvore
Podemos especificar a profundidade máxima da árvore utilizando o parâmetro max_depth.
"""

dt = DecisionTreeClassifier(max_depth=2)
dt.fit(X, y)

import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
plt.figure(figsize=(12,6))
_ = plot_tree(dt, feature_names=feature_names, class_names=target_names)

"""O código abaixo gera árvores de decisão com diferentes profundidades máximas e as avalia em termos de acurácia.

Observe que todas as árvores são treinadas e avaliadas com os mesmos conjuntos de treino e teste, visto que especificamos o parâmetro $random\_state = 0$.

Com base nesse código, e possíveis modificações que você faça a ele, responda à **Questão  4** do questionário.

**Não mude o valor que está sendo passado em random_state=0**.

"""

max_depths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, None]  # None faz com que essa poda não seja aplicada
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
for depth in max_depths:
  dt = DecisionTreeClassifier(max_depth=depth, random_state=0)
  dt.fit(X_train, y_train)

  y_pred = dt.predict(X_test)
  acc = accuracy_score(y_test, y_pred)
  print(acc)

"""### Exemplo de Pós-poda: Custo-complexidade

A biblioteca scikit-learn possui uma implementação de pós-poda por custo-complexidade, baseada no parâmetro de custo-complexidade $\alpha \ge 0$.

Na implementação descrita na biblioteca, é definido também um custo-complexidade efetivo do nodo. Quanto maior for a taxa de erros ao se podar a subárvore de um nodo, maior será seu custo-complexidade efetivo. Além disso, quanto maior for a complexidade (número de nodos terminais) da subárvore do nodo, menor será seu custo-complexidade efetivo.
Em resumo, um nodo com alto custo-complexidade efetivo é um nodo importante para diminuir a taxa de erros e com baixa complexidade.

Dentro da biblioteca, passamos um parâmetro $ccp\_alpha$ que serve como um custo-complexidade efetivo de corte: subárvores são podadas enquanto houver nodos com custo-complexidade menor do que o parâmetro $ccp\_alpha$.
Ou seja, quando maior for o parâmetro, mais intensa será a poda.

Para mais informações:
* https://scikit-learn.org/stable/modules/tree.html#minimal-cost-complexity-pruning
* https://scikit-learn.org/stable/auto_examples/tree/plot_cost_complexity_pruning.html

Use o código abaixo para resolver à **Questão 5**.
"""

def plot_acc_vs_ccp(accuracies_train, accuracies_test, ccps):
  fig, ax = plt.subplots(figsize=(8, 4))
  ax.set_xlabel("alpha")
  ax.set_ylabel("accuracy")
  ax.set_title("Accuracy vs alpha for training and testing sets")
  ax.plot(ccps, accuracies_train, marker="o", label="train", drawstyle="steps-post")
  ax.plot(ccps, accuracies_test, marker="o", label="test", drawstyle="steps-post")
  ax.legend()
  ax.grid()
  plt.show()


accs_train = []
accs_test = []
ccps = [k * 0.001 for k in range(0, 200, 2)]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
for ccp in ccps:
  dt = DecisionTreeClassifier(ccp_alpha=ccp, random_state=0)
  dt.fit(X_train, y_train)

  y_pred_train = dt.predict(X_train)
  acc_train = accuracy_score(y_train, y_pred_train)

  y_pred_test = dt.predict(X_test)
  acc_test = accuracy_score(y_test, y_pred_test)

  accs_train.append(acc_train)
  accs_test.append(acc_test)

plot_acc_vs_ccp(accs_train, accs_test, ccps)