# Exemplo de conexão do Vanna-IA com SQLite local usando OpenAI

# Importando as classes necessárias
from vanna.openai.openai_chat import OpenAI_Chat
from vanna.chromadb.chromadb_vector import ChromaDB_VectorStore
import sqlite3
import pandas as pd
import os

# Criando uma classe personalizada que combina OpenAI com ChromaDB
class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)
    
    # Método para conectar ao banco SQLite
    def connect_to_sqlite(self, db_path):
        """
        Conecta ao banco de dados SQLite no caminho especificado
        """
        self.db_path = db_path
        # Verifica se o arquivo do banco de dados existe
        if not os.path.exists(db_path):
            print(f"Criando novo banco de dados SQLite em: {db_path}")
        
        # Teste de conexão
        try:
            conn = sqlite3.connect(db_path)
            print(f"Conectado com sucesso ao banco SQLite: {db_path}")
            conn.close()
        except Exception as e:
            print(f"Erro ao conectar ao banco SQLite: {e}")
            return False
        
        return True
    
    # Método para executar consultas SQL no SQLite
    def run_sql(self, sql):
        """
        Executa a consulta SQL no banco de dados SQLite
        """
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Erro ao executar SQL: {e}")
            return None
    
    # Método para obter o esquema do banco de dados
    def get_schema(self):
        """
        Obtém o esquema do banco de dados SQLite para treinamento
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Consulta todas as tabelas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema = []
            for table in tables:
                table_name = table[0]
                # Pula tabelas do sistema SQLite
                if table_name.startswith('sqlite_'):
                    continue
                    
                # Obtém informações das colunas
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns = cursor.fetchall()
                
                # Constrói a definição CREATE TABLE
                create_stmt = f"CREATE TABLE {table_name} (\n"
                for i, col in enumerate(columns):
                    col_name = col[1]
                    col_type = col[2]
                    not_null = "NOT NULL" if col[3] else ""
                    is_pk = "PRIMARY KEY" if col[5] else ""
                    
                    create_stmt += f"    {col_name} {col_type} {not_null} {is_pk}"
                    if i < len(columns) - 1:
                        create_stmt += ",\n"
                    else:
                        create_stmt += "\n"
                
                create_stmt += ");"
                schema.append(create_stmt)
            
            conn.close()
            return "\n\n".join(schema)
        except Exception as e:
            print(f"Erro ao obter esquema: {e}")
            return ""

# Configuração principal
def main():
    # Substitua pela sua chave da API da OpenAI
    api_key = "GPT key"
    
    # Instanciando o Vanna
    vn = MyVanna(config={
        'api_key': api_key,
        'model': 'gpt-4'  # ou outro modelo compatível
    })
    
    # Caminho para o banco de dados SQLite
    db_path = "exemplo_banco.db"
    
    # Conecta ao banco SQLite
    if vn.connect_to_sqlite(db_path):
        # Se for um banco novo, vamos criar algumas tabelas de exemplo
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Cria tabelas de exemplo se não existirem
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT,
            data_cadastro TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER,
            data_venda TEXT,
            valor_total REAL,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY,
            venda_id INTEGER,
            produto_id INTEGER,
            quantidade INTEGER,
            preco_unitario REAL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        ''')
        
        # Insere alguns dados de exemplo
        # Clientes
        cursor.execute("INSERT OR IGNORE INTO clientes (id, nome, email, data_cadastro) VALUES (1, 'Maria Silva', 'maria@exemplo.com', '2023-01-15')")
        cursor.execute("INSERT OR IGNORE INTO clientes (id, nome, email, data_cadastro) VALUES (2, 'João Santos', 'joao@exemplo.com', '2023-02-20')")
        
        # Produtos
        cursor.execute("INSERT OR IGNORE INTO produtos (id, nome, preco, estoque) VALUES (1, 'Notebook', 3500.00, 10)")
        cursor.execute("INSERT OR IGNORE INTO produtos (id, nome, preco, estoque) VALUES (2, 'Smartphone', 1800.00, 15)")
        
        # Vendas
        cursor.execute("INSERT OR IGNORE INTO vendas (id, cliente_id, data_venda, valor_total) VALUES (1, 1, '2023-03-10', 3500.00)")
        cursor.execute("INSERT OR IGNORE INTO vendas (id, cliente_id, data_venda, valor_total) VALUES (2, 2, '2023-03-15', 1800.00)")
        
        # Itens de venda
        cursor.execute("INSERT OR IGNORE INTO itens_venda (id, venda_id, produto_id, quantidade, preco_unitario) VALUES (1, 1, 1, 1, 3500.00)")
        cursor.execute("INSERT OR IGNORE INTO itens_venda (id, venda_id, produto_id, quantidade, preco_unitario) VALUES (2, 2, 2, 1, 1800.00)")
        
        conn.commit()
        conn.close()
        
        # Obtém o esquema do banco para treinamento
        schema = vn.get_schema()
        print("Esquema do banco obtido para treinamento:")
        print(schema)
        
        # Treina o modelo com o esquema do banco
        vn.train(ddl=schema)
        
        # Adiciona documentação de negócios
        vn.train(documentation="""
        Nossa empresa vende produtos eletrônicos.
        Clientes são pessoas que fizeram pelo menos uma compra.
        Cada venda pode ter múltiplos itens de produtos diferentes.
        O valor total da venda é a soma dos preços unitários multiplicados pelas quantidades.
        """)
        
        # Adiciona exemplos de consultas SQL
        vn.train(sql="""
        SELECT c.nome, SUM(v.valor_total) as total_gasto
        FROM clientes c
        JOIN vendas v ON c.id = v.cliente_id
        GROUP BY c.nome
        ORDER BY total_gasto DESC
        """)
        
        # Exemplo de uso - gerar SQL a partir de uma pergunta
        pergunta = "Quais são os produtos mais vendidos?"
        sql_gerado = vn.generate_sql(pergunta)
        
        print("\nPergunta:", pergunta)
        print("SQL gerado:", sql_gerado)
        
        # Executa o SQL gerado
        resultado = vn.run_sql(sql_gerado)
        print("\nResultado:")
        print(resultado)
        
         # Exemplo de uso - gerar SQL a partir de uma pergunta
        pergunta = "Liste os clientes, e seus produtos e preço e a quantidade, que o valor unitário do produto seja acima de R$ 2000,00."
        sql_gerado = vn.generate_sql(pergunta)
        
        print("\nPergunta:", pergunta)
        print("SQL gerado:", sql_gerado)
        
        # Executa o SQL gerado
        resultado = vn.run_sql(sql_gerado)
        print("\nResultado:")
        print(resultado)

if __name__ == "__main__":
    main()


