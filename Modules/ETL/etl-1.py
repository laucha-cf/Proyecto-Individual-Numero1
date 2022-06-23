import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import Levenshtein as lev
sns.set()


dataset_names = ['df_clientes', 'df_compras', 'df_gastos', 'df_localidades','df_proveedores', 'df_sucursales', 'df_ventas', 'df_canalventa', 'df_tipogasto']


#Levantamos los datasets en crudo (archivos .csv)
df_clientes     =pd.read_csv('../Datasets/Clientes.csv'   , encoding='latin-1', sep=';')
df_compras      =pd.read_csv('../Datasets/Compra.csv'     , encoding='latin-1', sep=',')
df_gastos       =pd.read_csv('../Datasets/Gasto.csv'      , encoding='latin-1', sep=',')
df_localidades  =pd.read_csv('../Datasets/Localidades.csv', encoding='latin-1', sep=',')
df_proveedores  =pd.read_csv('../Datasets/Proveedores.csv', encoding='latin-1', sep=',')
df_sucursales   =pd.read_csv('../Datasets/Sucursales.csv' , encoding='latin-1', sep=';')
df_ventas       =pd.read_csv('../Datasets/Venta.csv'      , encoding='latin-1', sep=',')
df_canalventa   =pd.read_excel('../Datasets/CanalDeVenta.xlsx')
df_tipogasto    =pd.read_csv('../Datasets/TiposDeGasto.csv', encoding='latin-1', sep=',')

#Dataset de provincias normalizadas para utilizar luego
df_provincias = pd.read_csv('../Datasets/provincias.csv', sep=',', encoding='utf-8')
provincias_normalizadas = list(df_provincias['nombre_completo'].unique())


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
    cols_nuevas = ['categoria','lat','lon','idDepartamento','nombreDepartamento','fuente','idLocalidad','idLocalidadCensal','nombreLocalidadCensal','idMunicipio','nombreMunicipio','nombreLocalidad','idProvincia','nombreProvincia']
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
    df_clientes.drop(columns='col10', inplace=True)
    
    columnas = ['provincia', 'nom_y_ape', 'localidad', 'domicilio']
    for col in columnas:
        df_clientes[col] = df_clientes[col].str.title()

    df_clientes['edad'].fillna(int(df_clientes['edad'].mean()), inplace=True)
    df_clientes['edad'] = df_clientes['edad'].astype('int')
    
    df_clientes['lat'] = df_clientes['lat'].str.replace(',', '')
    df_clientes['long'] = df_clientes['long'].str.replace(',', '')
    df_clientes['lat'] = pd.to_numeric(df_clientes['lat'], errors='coerce', downcast='float')
    
    m = df_clientes['provincia'].isna()
    for prov_normal in provincias_normalizadas:
        for i, prov in enumerate(df_clientes.loc[(m==False),'provincia']):
            porc_parecido = lev.ratio(prov_normal.lower(), prov.lower())
            if (porc_parecido > 0.50):
                df_clientes['provincia'][i] = prov_normal


def etl_compras():
    pass