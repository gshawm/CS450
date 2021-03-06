from classifier import Classifier, get_accuracy
from node import Node


class NeuralNetwork(Classifier):
    def __init__(self, iterations):
        super().__init__()
        self.nodes = []
        self.iterations = iterations
        self.accuracies = []

    def train(self, dataset):
        #datasets = dataset.split_dataset(0.7)
        self.training_set = dataset
        #self.validation_set = datasets[1]

        #while True:
        for i in range(self.iterations):
            predictions = []
            for j in range(self.training_set.data.__len__()):
                prediction = self.__feed_forward(self.training_set.data[j])
                predictions.append(prediction)
                #print("PREDICTION: " + str(prediction))
                #print("REAL: " + str(self.training_set.target[j]))
                self.__set_targets(self.training_set.target[j])
                if prediction != self.training_set.target[j]:
                    #print("Bad prediction")
                    self.__back_propagate()
            accuracy = get_accuracy(predictions, self.training_set.target)
            self.accuracies.append(accuracy)
            #print("Current Accuracy: " + str(accuracy) + "%")
            self.training_set.randomize()

            #for i in range(self.validation_set.data.__len__()):
             #   pass

    def predict(self, dataset):
        self.testing_set = dataset
        predictions = []

        for i in range(dataset.data.__len__()):
            predictions.append(self.__feed_forward(self.testing_set.data[i]))

        return predictions

    def create_layered_network(self, num_nodes_on_layers: list, num_attributes):
        self.__create_layer(num_nodes_on_layers[0], num_attributes+1)
        for i in range(1,num_nodes_on_layers.__len__()):
            self.__create_layer(num_nodes_on_layers[i], num_nodes_on_layers[i-1]+1)

    def display_network(self):
        for i in range(self.nodes.__len__()):
            for j in range(self.nodes[i].__len__()):
                for k in range(i):
                    print("\t", end='')
                print(str(j) + str(self.nodes[i][j].weights))

    def __set_targets(self, correct_index):
        last_layer = self.nodes.__len__()-1
        for i in range(self.nodes[last_layer].__len__()):
            if i == correct_index:
                self.nodes[last_layer][i].target = 1
            else:
                self.nodes[last_layer][i].target = 0

    def __feed_forward(self, datapoint):
        self.__set_nodes_on_layer(0, datapoint)
        for j in range(self.nodes.__len__()-1):
            self.__calculate_nodes_on_layer(j)
            self.__set_nodes_on_layer(j+1, self.__get_outputs_on_layer(j))
        self.__calculate_nodes_on_layer(self.nodes.__len__()-1)
        prediction = self.__evaluate_outputs()

        return prediction

    def __back_propagate(self):
        # Loop through each layer
        for i in range(self.nodes.__len__()-1,-1,-1):
            # Loop through each node on each layer
            for j in range(self.nodes[i].__len__()):
                # Output Layer
                if i == self.nodes.__len__()-1:
                    # Compute the error of the output layer
                    self.nodes[i][j].compute_error(False)
                # Hidden Layer
                else:
                    weights = []
                    errors  = []

                    # Gather the errors and the weights of the nodes in the layer on the right
                    for k in range(self.nodes[i+1].__len__()):
                        errors.append(self.nodes[i+1][k].error)
                        weights.append(self.nodes[i+1][k].weights[j])

                    # Compute the error of the hidden layer
                    self.nodes[i][j].compute_error(True, weights, errors)
                prev_outputs = []

                # Gather outputs of the nodes in the layer on the left. If the node is an input or a bias node, get
                # the input instead.
                if i != 0:
                    prev_outputs.append(self.nodes[i][j].inputs[0])
                    for k in range(self.nodes[i-1].__len__()):
                        prev_outputs.append(self.nodes[i-1][k].output)
                else:
                    for k in range(self.nodes[i][j].inputs.__len__()):
                        prev_outputs.append(self.nodes[i][j].inputs[k])

                # Using the outputs of the nodes found in the layer on the left, update the weights of the current node.
                self.nodes[i][j].update_weights(prev_outputs)

    def __get_outputs_on_layer(self, layer):
        outputs = []
        for i in range(self.nodes[layer].__len__()):
            outputs.append(self.nodes[layer][i].output)
        return outputs

    def __set_nodes_on_layer(self, layer, inputs):
        for i in range(self.nodes[layer].__len__()):
            self.nodes[layer][i].set_inputs(inputs)

    def __create_layer(self, num_nodes, num_attributes): # num_inputs
        layer = []
        for i in range(num_nodes):
            node = Node()
            node.set_weights(num_attributes)
            layer.append(node)
        self.nodes.append(layer)

    def __calculate_nodes_on_layer(self, layer):
        for i in range(self.nodes[layer].__len__()):
            total = 0
            for j in range(self.nodes[layer][i].inputs.__len__()):
                total += self.nodes[layer][i].inputs[j]*self.nodes[layer][i].weights[j]
            self.nodes[layer][i].activation_function(total)

    def __evaluate_outputs(self):
        prediction = 0
        current_best = -999999999
        last_layer = self.nodes.__len__() - 1

        for i in range(self.nodes[last_layer].__len__()):
            if self.nodes[last_layer][i].output > current_best:
                prediction = i
                current_best = self.nodes[last_layer][i].output

        return prediction
