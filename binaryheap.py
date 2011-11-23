import math

class BinaryHeap:
	
	def __init__(self, costs):
		self.heap = [None]
		self.costs = costs
	
	def insert(self, node):
		self.heap.append(node)
		
		i = len(self.heap) - 1
		
		while i > 1 and self.getcost(self.heap[int(math.floor(i / 2))]) > self.getcost(self.heap[i]):
			temp = self.heap[i]
			self.heap[i] = self.heap[int(math.floor(i / 2))]
			self.heap[int(math.floor(i / 2))] = temp
			i = int(math.floor(i / 2))
			
			
	def getcost(self, node):
		return self.costs[node]

	def minimum(self):
		if len(self.heap) > 1:
			return self.heap[1]
		
		return None
	
	def extractminimum(self):
		
		if len(self.heap) < 2:
			return None
		
		minimum = self.heap[1]
		
		if len(self.heap) > 2:
			self.heap[1] = self.heap.pop()
			self.__heapify__()
		else:
			self.heap.pop()

		return minimum
		
	def fix(self, n):
		for i in range(1, len(self.heap)):
			if self.heap[i] == n:
				self.__heapify__(i)
				return
			
	
	def __heapify__(self, start = 1):
		i = start
		while i < len(self.heap):
			left = 2 * i
			right = 2 * i + 1
			largest = 0
			if left < len(self.heap) and self.getcost(self.heap[left]) <= self.getcost(self.heap[i]):
				largest = left
			else:
				largest = i
			
			if right < len(self.heap) and self.getcost(self.heap[right]) <= self.getcost(self.heap[largest]):
				largest = right
			
			if largest != i:
				temp = self.heap[i]
				self.heap[i] = self.heap[largest]
				self.heap[largest] = temp
				
				i = largest
			else:
				return
			
				
