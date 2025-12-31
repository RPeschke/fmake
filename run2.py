import numpy as np
import pandas as pd
import dataframe_helpers as dfh


class named_index:
    static_index = np.random.randint(100, 1000000)
    def __init__(self):
        self.current_index = named_index.static_index
        named_index.static_index += 1

        





def matrix_to_indexed_df(matrix):
    """
    Convert an N-dimensional matrix to an indexed DataFrame.
    
    Parameters:
    matrix: array-like, can be 1D, 2D, 3D, ..., ND
    
    Returns:
    DataFrame with columns: index1, index2, ..., indexN, value
    """
    matrix = np.array(matrix)
    shape = matrix.shape
    n_dims = len(shape)
    
    # Create index arrays for each dimension
    indices = np.indices(shape)
    
    # Create column names
    index_cols = [f'index{i+1}' for i in range(n_dims)]
    
    # Build the dataframe
    data = {}
    for i, col_name in enumerate(index_cols):
        data[col_name] = indices[i].ravel()
    data['value'] = matrix.ravel()
    
    return pd.DataFrame(data)


def matrix_elementwise_op(rhs, lhs, op):
            # Check if both have the same number of indices
        num_indices_self = len(rhs.array_type.columns) - 1
        num_indices_other = len(lhs.array_type.columns) - 1
        
        if num_indices_self != num_indices_other:
            raise ValueError(f"Cannot add matrices with different number of indices: {num_indices_self} vs {num_indices_other}")
        
        # Get the column names (excluding 'value')
        cols_self = [col for col in rhs.array_type.columns if col != "value"]
        cols_other = [col for col in lhs.array_type.columns if col != "value"]
        
        # Rename other's columns to match self's columns if they differ
        if cols_self != cols_other:
            other_renamed = lhs.array_type.copy()
            rename_dict = {cols_other[i]: cols_self[i] for i in range(len(cols_self))}
            other_renamed = other_renamed.rename(columns=rename_dict)
        else:
            other_renamed = lhs.array_type
        
        # Merge on the index columns
        df = rhs.array_type.merge(other_renamed, on=cols_self, how='outer', suffixes=('_x', '_y'))
        
        # Fill NaN values with 0 for addition
        df['value_x'] = df['value_x'].fillna(0)
        df['value_y'] = df['value_y'].fillna(0)
        
        # Add the values
        df["value"] = op(df["value_x"], df["value_y"])

        df = df.drop(["value_x", "value_y"], axis=1)
        
        return named_index_matrix(df)
    

class named_index_matrix:
    def __init__(self, array_type):
        if isinstance(array_type, pd.DataFrame):
            self.array_type = array_type.copy()
        else:
            self.array_type = matrix_to_indexed_df(array_type)
        self.index_list = []
    
    def __repr__(self):
        num_cols = len(self.array_type.columns)
        num_index_cols = num_cols - 1  # Subtract 1 for 'value' column
        
        # Single column (just value) - treat as scalar
        if num_index_cols == 0:
            value = self.array_type['value'].iloc[0]
            return f"{value}"
        
        # One index column - treat as vector
        elif num_index_cols == 1:
            vector = self.array_type['value'].values
            return f"Vector:\n{vector}"
        
        # Two index columns - treat as matrix
        elif num_index_cols == 2:
            matrix = indexed_df_to_matrix_2d(self.array_type)
            return f"Matrix:\n{matrix}"
        
        # More than 2 index columns - display as DataFrame
        else:
            return f"Tensor (DataFrame):\n{self.array_type}"
    
    def __str__(self):
        return self.__repr__()
    
    def __call__(self, *index_list):
        if len(self.array_type.columns ) != len(index_list) +1 :
            raise ValueError("Length of index_list must match number of columns")
        self.array_type.columns  = [x.current_index for x in  index_list] + ["value"]
        return named_index_matrix(self.array_type.copy())
    
    def __add__(self, other):
        return matrix_elementwise_op(self, other, lambda x, y: x + y)

    def __sub__(self, other):
        return matrix_elementwise_op(self, other, lambda x, y: x - y)
    
    @property
    def T(self):

        df = self.array_type.copy()
        cols = df.columns.tolist()
        cols[0], cols[1] = cols[1], cols[0]
        df = df.reindex(columns=cols)
        return named_index_matrix(df)
        
      
    def __mul__(self, other):
        # Handle scalar multiplication (int or float)
        if isinstance(other, (int, float)):
            df = self.array_type.copy()
            df['value'] = df['value'] * other
            return named_index_matrix(df)

        # Handle matrix multiplication
        common = list(set(self.array_type.columns ) & set(other.array_type.columns ))
        common = list(filter(lambda x: "value" not in str(x), common))

        if len(common) ==0:
            df = self.array_type.merge(other.array_type, how='cross')
        else:
            df = self.array_type.merge(other.array_type, on=common, how='inner') 

        df["value"] = df["value_x"]*df["value_y"]
        df = df.drop(["value_x", "value_y"], axis=1)

        col = [x for x in df.columns if x != "value"]

        for i in common:
            col = list(filter(lambda x: x != i, col))
            if len(col) ==0:
                df = pd.DataFrame( {"value": [np.sum(df["value"])]})
            else:
                df = dfh.group_apply(
                        df, 
                        col, 
                        ["value"], 
                        lambda x: np.sum(x["value"])
                        )
        return named_index_matrix(df)
    
    def __rmul__(self, other):
        # Handle right multiplication for scalar * matrix
        if isinstance(other, (int, float)):
            return self.__mul__(other)
        return NotImplemented



def indexed_df_to_matrix_2d(df):
    """Convert 2D indexed DataFrame back to matrix"""
     
    return df.pivot(index=df.columns[0], columns=df.columns[1], values='value').values

mu = named_index() 
nu = named_index() 
ro  = named_index() 
x1 = named_index()
x2 = named_index()


g = pd.DataFrame( np.transpose([[0 ,0, 0, 0, 1 ,1, 1, 1, 2 ,2, 2, 2, 3 ,3, 3, 3], [0 ,1, 2, 3, 0 ,1, 2, 3, 0 ,1, 2, 3, 0 ,1, 2, 3],[1 ,0, 0, 0, 0 ,-1, 0, 0, 0 ,0, -1, 0, 0 ,0, 0, -1]]))
g1 = named_index_matrix(g) 
g2 = named_index_matrix(g) 
g3 = g1( mu, nu) * g2( mu, nu)
m = named_index_matrix([0, 1,2])


m1 = m(mu)*m(nu)


a =  named_index_matrix([1, 0,2])(x1)
b = named_index_matrix([0, 1,-1])(x1)
c = named_index_matrix([0, 1,1])(x2)
d = named_index_matrix([-1, 2,2])(x2)

print(
     a * 
      (b * c) * 
      d
      )
print( (a * b ) 
      * (c *  d))


print(  c * a * 
        d * b 
      
      
      )


print(indexed_df_to_matrix_2d(m1.array_type))
print("hello")


