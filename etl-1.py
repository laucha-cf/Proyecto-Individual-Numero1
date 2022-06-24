import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import Levenshtein as lev
sns.set()

#Levantamos los datasets en crudo (archivos .csv)
df_clientes     =pd.read_csv('./Modules/Datasets/Clientes.csv'   , encoding='latin-1', sep=';')
df_compras      =pd.read_csv('./Modules/Datasets/Compra.csv'     , encoding='latin-1', sep=',')
df_gastos       =pd.read_csv('./Modules/Datasets/Gasto.csv'      , encoding='latin-1', sep=',')
df_localidades  =pd.read_csv('./Modules/Datasets/Localidades.csv', encoding='latin-1', sep=',')
df_proveedores  =pd.read_csv('./Modules/Datasets/Proveedores.csv', encoding='latin-1', sep=',')
df_sucursales   =pd.read_csv('./Modules/Datasets/Sucursales.csv' , encoding='latin-1', sep=';')
df_ventas       =pd.read_csv('./Modules/Datasets/Venta.csv'      , encoding='latin-1', sep=',')
df_canalventa   =pd.read_excel('./Modules/Datasets/CanalDeVenta.xlsx')
df_tipogasto    =pd.read_csv('./Modules/Datasets/TiposDeGasto.csv', encoding='latin-1', sep=',')

#Datasets de provincias y localidades normalizadas para utilizar luego
df_provincias = pd.read_csv('./Modules/Datasets/provincias.csv', sep=',', encoding='utf-8')
df_loc_normales = pd.read_csv('./Modules/Datasets/localidades_normalizadas.csv', sep=',', encoding='utf-8')

provincias_normalizadas = list(df_provincias['nombre_completo'].unique())
localidades_normalizadas = list(df_loc_normales['localidad_censal_nombre'].unique())


def renombrarColumnas():
    #Clientes
    cols_nuevas = ['idCliente','provincia', 'nom_y_ape', 'domicilio', 'tel', 'edad', 'localidad', 'lat', 'long', 'col10']
    df_clientes.columns = cols_nuevas

    #Compras
    cols_nuevas = ['idCompra','fecha', 'año', 'mes', 'periodo', 'idProducto','cantidad', 'precio', 'idProveedor']
    df_compras.columns = cols_nuevas

    #Gastos
    cols_nuevas = ['idGasto', 'idSucursal', 'idTipoGasto', 'fecha', 'monto']
    df_gastos.columns = cols_nuevas

    #Localidades
    cols_nuevas = ['categoria','lat','long','idDepartamento','nombreDepartamento','fuente','idLocalidad','idLocalidadCensal','nombreLocalidadCensal','idMunicipio','nombreMunicipio','nombreLocalidad','idProvincia','nombreProvincia']
    df_localidades.columns = cols_nuevas

    #Proveedores
    cols_nuevas = ['idProveedor','nombre', 'direccion', 'ciudad', 'estado', 'pais', 'departamento']
    df_proveedores.columns = cols_nuevas

    #Sucursales
    cols_nuevas = ['idSucursal','sucursal', 'direccion', 'localidad', 'provincia', 'lat', 'long']
    df_sucursales.columns = cols_nuevas

    #Ventas
    cols_nuevas = ['idVenta','fechaVenta','fechaEntrega','idCanal','idCliente','idSucursal','idEmpleado','idProducto','precio','cantidad']
    df_ventas.columns = cols_nuevas

    #Tipo de Gasto
    cols_nuevas = ['idTipoGasto', 'descripcion', 'montoAprox']
    df_tipogasto.columns = cols_nuevas

    #Canal de Venta
    cols_nuevas = ['codigo', 'descripcion']
    df_canalventa.columns = cols_nuevas

def etl_clientes():
    global df_clientes
    df_clientes = df_clientes.drop(columns='col10')
    
    columnas = ['provincia', 'nom_y_ape', 'localidad', 'domicilio']
    for col in columnas:
        df_clientes[col] = df_clientes[col].str.title()

    df_clientes['edad'].fillna(int(df_clientes['edad'].mean()), inplace=True)
    df_clientes['edad'] = df_clientes['edad'].astype('int')
    
    df_clientes['lat'] = df_clientes['lat'].str.replace(',', '')
    df_clientes['long'] = df_clientes['long'].str.replace(',', '')
    df_clientes['lat'] = pd.to_numeric(df_clientes['lat'], errors='coerce', downcast='float')
    
    m = df_clientes['provincia'].notna()
    provincias_unicas = list(df_clientes.loc[m, 'provincia'].unique())
    for prov_normal in provincias_normalizadas:
        for prov_dataset in provincias_unicas:
            porc_parecido = lev.ratio(prov_normal.lower(), prov_dataset.lower())
            if porc_parecido >= 0.40:
                df_clientes.loc[(df_clientes['provincia']==prov_dataset), 'provincia'] = prov_normal
    
    df_clientes = df_clientes.dropna(thresh=7)

def etl_compras():
    df_compras['precio'].fillna(df_compras['precio'].mean(), inplace=True)
    
    df_compras['precio'] = df_compras['precio'].astype('float')
    
    cols = ['idCompra', 'año', 'mes', 'periodo', 'idProducto', 'cantidad', 'idProveedor']
    for col in cols:
        m = ((df_compras[col].isna()) | (df_compras[col]==''))
        df_compras.loc[ (m==False), col] = df_compras[col].astype('int')

def etl_ventas():
    df_ventas['precio'].fillna(df_ventas['precio'].mean(), inplace=True)
    
    df_ventas['cantidad'].fillna(int(df_ventas['cantidad'].mean()), inplace=True)

def outliers():
    #Deteccion outliers
    dataset_names = [df_compras, df_ventas]
    dicc = {True:1, False:0}
    for df in dataset_names:
        promedio = df['precio'].mean()
        std_dev = df['precio'].std()
        minimo = 0
        maximo = promedio + 3 * std_dev
        mascara_outlier = ((df['precio']<minimo) | (df['precio']>maximo))
        df['Outlier'] = mascara_outlier.map(dicc)

        promedio = df['cantidad'].mean()
        std_dev = df['cantidad'].std()
        minimo = 0
        maximo = promedio + 3 * std_dev
        mascara_outlier = ((df['cantidad']<minimo) | (df['cantidad']>maximo))
        df.loc[mascara_outlier, 'Outlier'] = 2
    
    #Reemplazamos outliers de precio por la media
    m = (df_ventas['Outlier'] == 1)
    df_ventas.loc[m, 'precio'] = df_ventas['precio'].mean()
    df_ventas.loc[m, 'Outlier'] = 0
    
    #Reemplazamos Outliers de cantidad por la division de este campo por 10 (considerando que hay un 0 de más)
    m = (df_ventas['Outlier'] == 2)
    df_ventas.loc[m, 'cantidad'] = df_ventas['cantidad']/10
    df_ventas.loc[m, 'Outlier'] = 0

def localidades():
    df_localidades['lat'] = df_localidades['lat'].astype(str)
    df_localidades['long'] = df_localidades['long'].astype(str)

    df_localidades['lat'] = df_localidades['lat'].str.replace('.', '')
    df_localidades['long'] = df_localidades['long'].str.replace('.', '')

    df_localidades['lat'] = pd.to_numeric(df_localidades['lat'], errors='coerce', downcast='float')
    df_localidades['long'] = pd.to_numeric(df_localidades['long'], errors='coerce', downcast='float')
    
    df_localidades['nombreLocalidad'] = df_localidades['nombreLocalidad'].str.title()
    
    provincias_unicas = list(df_localidades['nombreProvincia'].unique())
    
    for prov_normal in provincias_normalizadas:
        for prov_dataset in provincias_unicas:
            porc_parecido = lev.ratio(prov_normal.lower(), prov_dataset.lower())
            if porc_parecido >= 0.40:
                df_localidades.loc[(df_localidades['nombreProvincia']==prov_dataset), 'nombreProvincia'] = prov_normal

def proveedores():
    df_proveedores['direccion'] = df_proveedores['direccion'].str.title()
    df_proveedores['ciudad'] = df_proveedores['ciudad'].str.title()
    df_proveedores['estado'] = df_proveedores['estado'].str.title()
    df_proveedores['pais'] = df_proveedores['pais'].str.title()
    df_proveedores['departamento'] = df_proveedores['departamento'].str.title()

def sucursal():
    df_sucursales['direccion'] = df_sucursales['direccion'].str.title()
    
    localidades_unicas = df_sucursales['localidad'].unique()
    for loc_normal in localidades_normalizadas:
        for loc_dataset in localidades_unicas:
            porc_parecido = lev.ratio(loc_normal.lower(), loc_dataset.lower())
            if porc_parecido >= 0.50:
                df_sucursales.loc[(df_sucursales['localidad']==loc_dataset), 'localidad'] = loc_normal
    
    provincias_unicas = list(df_sucursales['provincia'].unique())
    for prov_normal in provincias_normalizadas:
        for prov_dataset in provincias_unicas:
            porc_parecido = lev.ratio(prov_normal.lower(), prov_dataset.lower())
            if porc_parecido >= 0.40:
                df_sucursales.loc[(df_sucursales['provincia']==prov_dataset), 'provincia'] = prov_normal

renombrarColumnas()
etl_clientes()
etl_compras()
etl_ventas()
outliers()
localidades()
proveedores()
sucursal()

