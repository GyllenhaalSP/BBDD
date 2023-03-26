"""
 By GyllenhaalSP mar 2023 @ https://github.com/GyllenhaalSP.
"""

# Queries de SQL para las consultas de la aplicación

def query_lista_productos():
    return f"""SELECT COD_PROD, NOM_PROD, I.IVA_POR AS IVA, CONCAT(TO_CHAR(PRECIO, '0.99'), ' EUROS') AS PRECIO 
    FROM PRODUCTO P, IVA I
    WHERE P.COD_IVA = I.COD_IVA
    ORDER BY COD_PROD
    """


def query_cliente(compare_string, table, abbreviation, column):
    if table == "CAB_PED":
        return f"""SELECT NOM_CLI 
        FROM CLIENTE C, {table} {abbreviation}
        WHERE UPPER({column}) LIKE UPPER('{compare_string}')
        AND C.DNI = {abbreviation}.DNI
        """
    elif table == "CAB_ALB":
        return f"""SELECT NOM_CLI 
        FROM CLIENTE C, CAB_PED P, {table} {abbreviation}
        WHERE UPPER({column}) LIKE UPPER('{compare_string}')
        AND C.DNI = P.DNI
        AND P.N_PED = {abbreviation}.N_PED 
        """
    elif table == "CAB_FACT":
        return f"""SELECT DISTINCT C.NOM_CLI 
        FROM CLIENTE C, CAB_PED CP, CAB_ALB CA, CAB_FACT CF
        WHERE UPPER(CF.N_FACT) LIKE UPPER('{compare_string}')
        AND C.DNI = CP.DNI
        AND CP.N_PED = CA.N_PED
        AND CA.N_FACT = CF.N_FACT
        """


def query_dir(compare_string, table, abbreviation, column):
    if table == "CAB_PED":
        return f"""SELECT C.CALLE, C.NUM, C.CP, C.PROV, C.CCAA 
        FROM CLIENTE C, {table} {abbreviation}
        WHERE UPPER({column}) LIKE UPPER('{compare_string}')
        AND C.DNI = {abbreviation}.DNI
        """
    elif table == "CAB_ALB":
        return f"""SELECT C.CALLE, C.NUM, C.CP, C.PROV, C.CCAA 
        FROM CLIENTE C, CAB_PED P, {table} {abbreviation}
        WHERE UPPER({column}) LIKE UPPER('{compare_string}')
        AND C.DNI = P.DNI
        AND P.N_PED = {abbreviation}.N_PED
        """
    elif table == "CAB_FACT":
        return f"""SELECT DISTINCT C.CALLE, C.NUM, C.CP, C.PROV, C.CCAA 
        FROM CLIENTE C, CAB_PED CP, CAB_ALB CA, CAB_FACT CF
        WHERE UPPER(CF.N_FACT) LIKE UPPER('{compare_string}')
        AND C.DNI = CP.DNI
        AND CP.N_PED = CA.N_PED
        AND CF.N_FACT = CA.N_FACT
        """


def query_productos(compare_string, table, abbreviation, column):
    if table == "CAB_PED":
        return f"""SELECT P.NOM_PROD, {abbreviation}.CANT, CONCAT(TO_CHAR(P.PRECIO, '99990.99'), ' EUROS') "PRECIO UNITARIO"
        FROM PRODUCTO P, {column} {abbreviation}
        WHERE UPPER({abbreviation}.N_PED) LIKE UPPER('{compare_string}')
        AND P.COD_PROD = {abbreviation}.COD_PROD
        ORDER BY {abbreviation}.N_LIN
        """
    elif table == "CAB_ALB":
        return f"""SELECT P.NOM_PROD, {abbreviation}.CANT, CONCAT(TO_CHAR(P.PRECIO, '99990.99'), ' EUROS') "PRECIO UNITARIO"
        FROM PRODUCTO P, {column} {abbreviation}
        WHERE UPPER ({abbreviation}.N_ALB) LIKE UPPER('{compare_string}')
        AND P.COD_PROD = {abbreviation}.COD_PROD
        ORDER BY {abbreviation}.N_LIN
        """


def query_factura(compare_string):
    return f"""SELECT DISTINCT P.NOM_PROD,I.IVA_POR, LA.CANT, 
    TO_CHAR(P.PRECIO, '990.99') AS PRECIO,
    ROUND((P.PRECIO * LA.CANT), 2) AS TOTAL,
    ROUND(((P.PRECIO * LA.CANT) * I.IVA), 2) AS "TOTAL CON IVA"
    FROM IVA I, PRODUCTO P, LIN_ALB LA, CAB_FACT CF, CAB_ALB CA, CAB_PED CP, CLIENTE C
    WHERE UPPER(CF.N_FACT) LIKE UPPER('{compare_string}')
    AND I.COD_IVA = P.COD_IVA
    AND P.COD_PROD = LA.COD_PROD
    AND CF.N_FACT = CA.N_FACT
    AND CA.N_ALB = LA.N_ALB
    AND CP.N_PED = CA.N_PED
    AND C.DNI = CP.DNI
    ORDER BY I.IVA_POR
    """
