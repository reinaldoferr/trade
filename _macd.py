# solo esta hace falta
import pandas as pd

from _technical_indicator import TechnicalIndicator

class Macd(TechnicalIndicator):

    def __init__(self, input_data: pd.DataFrame, src='Close', fast=12, slow=26, smooth=9): 

        """
        Parameters:
        input_data: source data, type pandas.DataFrame
        src: 'Close', 'Open', etc.(default=Close), type String
        fast: MACD moving average (default=12), type Tnteger
        slow: MACD Signal moving average(default=26), type Tnteger
        smooth: Smooth moving average(default=9), type Tnteger
        """

        # Set members values
        self.src = src
        self.fast = fast
        self.slow = slow
        self.smooth = smooth

        #self.input_data = input_data.copy()
        # Control is passing to the parent class
        super().__init__(calling_instance=self.__class__.__name__,
                         input_data=input_data)

        # Calcutate MACD (no hace falta lo hace las Super Class)
        #self.__calculate()

        # Calculate Signal buy & Sell (no hace falta lo hace las Super Class)
        #self.__calculate_buy_sell()



    # Calculate MACD
    def _calculateTi(self):

        """
        Calculates the technical indicator for the given input data.
        Put values into pandas.DataFrame
        """
        
        data = pd.DataFrame(index=self._input_data.index, 
                            columns=['MACD','Signal line','MACD Hist'], 
                            data=0, dtype='float64')


        data['MACD'] = self._input_data[self.src].ewm(span=self.fast, min_periods=self.fast, adjust=False).mean() - self._input_data[self.src].ewm(span=self.slow, min_periods=self.slow, adjust=False).mean().round(4)
       
        data['Signal line'] = data['MACD'].ewm(span=self.smooth, min_periods=self.smooth, adjust=False).mean().round(4)
       
        data['MACD Hist'] = data['MACD'] - data['Signal line']

        return data.astype(dtype='float64', errors='ignore')


    # Calculate MACD
    def _calculateBuySell(self):

        """
        Calculates and returns the trading signal for the calculated technical
        indicator.

        Returns:
            Create a new pandas.DataFrame: _ti_buysell_data
            0 hold, -1 buy, 1  sell: The calculated trading
            signal.
        """

        data = pd.DataFrame(index=self._input_data.index, 
                            columns=['MACD Above Zero','MACD Crossover','MACD Below Zero','MACD Crossunder'], 
                            data=0, dtype='int')

        # Not enough data for calculating trading signal
        if len(self._input_data.index) < 2:
            
            data['MACD Above Zero'] = 0.0
            data['MACD Crossover'] = 0.0
            data['MACD Below Zero'] = 0.0
            data['MACD Crossunder'] = 0.0

        else:    
            
            # MACD rises above zero 
            cond1 = self._ti_data.shift(periods=1)['MACD'] < 0 
            cond2 = self._ti_data.shift(periods=1)['MACD'] < self._ti_data['MACD']
            above_zero = cond1 & cond2 

            # MACD rises above Signal Line
            cond3 = self._ti_data.shift(periods=1)['MACD'] < self._ti_data.shift(periods=1)['Signal line']
            cond4 = self._ti_data['MACD'] > self._ti_data['Signal line']
            crossover = cond3 & cond4
          
            data['MACD Above Zero'] = above_zero.astype(int)
            data['MACD Crossover'] = crossover.astype(int)

            # MACD fall below zero 
            cond1 = self._ti_data.shift(periods=1)['MACD'] > 0 
            cond2 = self._ti_data.shift(periods=1)['MACD'] > self._ti_data['MACD']
            below_zero = cond1 & cond2 

            # MACD falls below Signal Line}
            cond3 = self._ti_data.shift(periods=1)['MACD'] > self._ti_data.shift(periods=1)['Signal line']
            cond4 = self._ti_data['MACD'] < self._ti_data['Signal line']
            crossunder = cond3 & cond4

            data['MACD Below Zero'] = below_zero.astype(int)
            data['MACD Crossunder'] = crossunder.astype(int)
        
        return data.astype(dtype='int', errors='ignore')

    '''
    Quedó la del SuperClase
    def getData(self) -> pd.DataFrame:

        """
        Returns:
            pandas.DataFrame: The calculated indicator. Index is of type
            ``pandas.DatetimeIndex``. It contains three columna, the ``MACD``, 
             ``Signal line`` &  ``MACD Hist``.
        """

        return self._ti_data
    '''


    '''
    Quedó la del SuperClase
    def getDataConcat(self) -> pd.DataFrame:
        
        """
        Concat the Source in data_df of type ``pandas.DatetimeIndex``
        with calculates the technical indicator.

        Returns:
            pandas.DataFrame: Source Data concat with the calculated indicator. 
            Index is of type: ``pandas.DatetimeIndex``. 
        """

        # Concat original pandas.DataFrame with indicator pandas.DataFrame
        #frames = [df1, df2, df3]
        #result = pd.concat(frames)
        #return pd.concat([self.input_data, self.getData()], ignore_index=True)
        return pd.merge(self.input_data, self._ti_data, how='inner', left_index=True, right_index=True)
    '''
    

    '''
    def getSignal(self) -> pd.DataFrame:

        """
        Calculates and returns the trading signal for the calculated technical
        indicator.

        Returns:
            pandas.DataFrame:
            0 hold, -1 buy, 1  sell: The calculated trading
            signal.
        """

        return self._ti_buysell_data
    '''

    '''
    def getSignalConcat(self) -> pd.DataFrame:
        
        """
        Concat the Source in data_df of type ``pandas.DatetimeIndex``
        with calculates signal buy & sell.

        Returns:
            pandas.DataFrame: Source Data concat with the calculated indicator. 
            Index is of type: ``pandas.DatetimeIndex``. 
        """
        return pd.merge(self.input_data, self._ti_buysell_data, how='inner', left_index=True, right_index=True)
    '''

    '''
    def getAllConcat(self) -> pd.DataFrame:
        
        """
        Concat the Source in data_df of type ``pandas.DatetimeIndex``
        with calculates the technical indicator & buy & sell signal.

        Returns:
            pandas.DataFrame: Source Data concat with the calculated indicator. 
            Index is of type: ``pandas.DatetimeIndex``. 
        """
        temp_df = pd.merge(self.input_data, self._ti_data, how='inner', left_index=True, right_index=True) 
        return pd.merge(temp_df, self._ti_buysell_data, how='inner', left_index=True, right_index=True)    
    '''