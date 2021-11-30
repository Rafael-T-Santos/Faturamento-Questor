import pyodbc
import pyautogui
import time

#Digite 'IP,PORTA'
server = 'tcp:192.168.0.1,1122' 
database = 'banco' 
username = 'usuario' 
password = 'senha' 
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#Insert
cursor.execute("""INSERT INTO TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO (CD_LANCAMENTO,CD_FORMA_PAGAMENTO,CD_CARTEIRA,VL_VALOR,VL_VALOR_MOEDA,DT_CADASTRO,DT_ATUALIZACAO,CD_USUARIO,CD_USUARIOAT,NR_TIPO_PAGAMENTO)                                                     
                       SELECT TBL_NOTAS_FATURAMENTO.CD_LANCAMENTO, 
                              TBL_NOTAS_FATURAMENTO.CD_FORMA_PAGAMENTO, 
                           ISNULL(iif(COUNT(TBL_NOTAS_FATURAMENTO_PARCELAS.CD_ID) > 0,MIN(TBL_NOTAS_FATURAMENTO_PARCELAS.CD_CARTEIRA),TBL_NOTAS_FATURAMENTO.CD_CARTEIRA),TBL_NOTAS_FATURAMENTO.CD_CARTEIRA), 
                           ISNULL(SUM(TBL_NOTAS_FATURAMENTO_PARCELAS.VL_PARCELA),TBL_NOTAS_FATURAMENTO.VL_TOTAL), 
                           ISNULL(SUM(TBL_NOTAS_FATURAMENTO_PARCELAS.VL_PARCELA_MOEDA),0), 
                           CURRENT_TIMESTAMP, 
                           CURRENT_TIMESTAMP, 
                           0, 
                           0, 
                              iif(COUNT(TBL_NOTAS_FATURAMENTO_PARCELAS.CD_ID) > 0,1,0)                                                     
                       FROM TBL_NOTAS_FATURAMENTO 
                       LEFT JOIN TBL_NOTAS_FATURAMENTO_PARCELAS ON TBL_NOTAS_FATURAMENTO_PARCELAS.CD_LANCAMENTO = TBL_NOTAS_FATURAMENTO.CD_LANCAMENTO 
                       INNER JOIN TBL_FINANCEIRO_FORMAS_PAGAMENTO ON TBL_FINANCEIRO_FORMAS_PAGAMENTO.CD_FORMA_PAGAMENTO = TBL_NOTAS_FATURAMENTO.CD_FORMA_PAGAMENTO                                                            
              LEFT JOIN TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO ON TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO.CD_LANCAMENTO = TBL_NOTAS_FATURAMENTO.CD_LANCAMENTO 
              WHERE TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO.CD_LANCAMENTO is null           
                       GROUP BY TBL_NOTAS_FATURAMENTO.CD_LANCAMENTO, 
                                TBL_NOTAS_FATURAMENTO.CD_FORMA_PAGAMENTO,                            
                           CD_TIPO_PAGAMENTO, 
                           X_TEF, 
                           X_TEF_POS, 
                  TBL_NOTAS_FATURAMENTO.CD_CARTEIRA     , 
                  TBL_NOTAS_FATURAMENTO.VL_TOTAL                   """)
cnxn.commit()

time.sleep(1)

#Update
cursor.execute("""UPDATE TBL_NOTAS_FATURAMENTO_PARCELAS  
    SET TBL_NOTAS_FATURAMENTO_PARCELAS.CD_PAGAMENTO = TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO.CD_PAGAMENTO 
 FROM TBL_NOTAS_FATURAMENTO_PARCELAS 
 INNER JOIN TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO on TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO.CD_LANCAMENTO = TBL_NOTAS_FATURAMENTO_PARCELAS.CD_LANCAMENTO 
 WHERE TBL_NOTAS_FATURAMENTO_PARCELAS.CD_PAGAMENTO is null AND TBL_NOTAS_FATURAMENTO_PARCELAS.CD_LANCAMENTO in (select CD_LANCAMENTO  
                                                                                                                from TBL_NOTAS_FATURAMENTO_PARCELAS   
                                                                                                                group by CD_LANCAMENTO 
                                                                                                                HAVING count(CD_PAGAMENTO) = 0) 
  """)
cnxn.commit()

time.sleep(1)

#Delete
cursor.execute("""DELETE parcelas 
 FROM TBL_NOTAS_FATURAMENTO_PARCELAS parcelas 
  INNER JOIN TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO on TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO.CD_LANCAMENTO = parcelas.CD_LANCAMENTO  
  WHERE TBL_NOTAS_FATURAMENTO_FORMAS_PAGAMENTO.CD_PAGAMENTO IS NOT NULL AND 
        parcelas.CD_PAGAMENTO is null and 
        parcelas.CD_LANCAMENTO in (select CD_LANCAMENTO  
                                   from TBL_NOTAS_FATURAMENTO_PARCELAS   
                                   group by CD_LANCAMENTO 
                                   HAVING count(CD_PAGAMENTO) > 0) """)
cnxn.commit()

time.sleep(1)

pyautogui.alert(text='Script realizado com sucesso, pressione OK e tente emitir o relatório novamente.', title='Script Faturamento', button='OK')
