# 🔍 Exemplo: Integração Vanna.AI com SQLite Local usando OpenAI

Este repositório demonstra como integrar a [Vanna.AI](https://www.vanna.ai/) com um banco de dados **SQLite local**, utilizando **OpenAI** para gerar consultas SQL a partir de linguagem natural. Também utiliza o **ChromaDB** como mecanismo de vetores para treinamento semântico.

---

## 📦 Tecnologias Utilizadas

- [Python](https://www.python.org/)
- [Vanna.AI](https://www.vanna.ai/)
- [OpenAI GPT-4](https://platform.openai.com/)
- [ChromaDB](https://www.trychroma.com/)
- [SQLite](https://www.sqlite.org/)
- [Pandas](https://pandas.pydata.org/)

---

## 🚀 Como Funciona

Este projeto:

1. Cria uma classe personalizada `MyVanna`, que herda funcionalidades de `ChromaDB_VectorStore` e `OpenAI_Chat`.
2. Conecta a um banco de dados SQLite local.
3. Cria tabelas de exemplo (clientes, produtos, vendas, itens_venda).
4. Insere dados fictícios.
5. Obtém e treina o modelo com o esquema do banco e informações de negócio.
6. Permite gerar consultas SQL automaticamente com base em perguntas feitas em linguagem natural.
7. Executa as queries geradas no banco de dados e imprime os resultados.

---

## 🧪 Exemplo de Uso

### Pergunta:
```txt
Quais são os produtos mais vendidos?
```

### SQL gerado:
```sql
SELECT p.nome, SUM(iv.quantidade) AS total_vendido
FROM itens_venda iv
JOIN produtos p ON iv.produto_id = p.id
GROUP BY p.nome
ORDER BY total_vendido DESC
```

---

## 📁 Estrutura do Projeto

```
├── vanna_sqlite_openai.py  # Código principal
└── exemplo_banco.db        # Banco de dados SQLite (criado na primeira execução)
```

---

## ⚙️ Pré-requisitos

- Python 3.8+
- Conta na [OpenAI](https://platform.openai.com/) com chave de API válida
- Instale as dependências:

```bash
pip install openai vanna chromadb pandas
```

---

## 🧠 Como Usar

1. **Configure sua chave da OpenAI** no arquivo `main()`:
   ```python
   api_key = "sua-api-key"
   ```

2. **Execute o script**:

   ```bash
   python vanna_sqlite_openai.py
   ```

3. O sistema irá:
   - Criar o banco de dados (se não existir)
   - Criar tabelas e inserir dados
   - Treinar o modelo com o esquema e documentação
   - Gerar SQLs automaticamente com base em perguntas
   - Executar e imprimir os resultados das consultas

---

## 📘 Exemplos de Perguntas Suportadas

- Quais são os produtos mais vendidos?
- Liste os clientes, seus produtos comprados e o valor unitário acima de R$ 2000,00.
- Quanto cada cliente gastou?
- Quais vendas ocorreram em março?

---
