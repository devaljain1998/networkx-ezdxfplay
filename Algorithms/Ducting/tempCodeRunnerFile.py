    def create_hash(type, number):
        """
        returns hash values for nodes of the graph
        """
        if type == 'Entity':
            return 'E'+str(number)
        elif type == 'Joint':
            return 'J'+str(number)
        else:
            return str(number)
