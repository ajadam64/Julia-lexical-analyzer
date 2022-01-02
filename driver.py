import lex
import sys

def main():
	#Code section gets file name from cli-arguments (if any), opens it and instantiates a new lex class with the source code file
	file = sys.stdin
	if len(sys.argv) > 1:
		try:
			source = open(sys.argv[1], "r")
			lexed = lex.lex(source)
			lexed.printTable()
			source.close()
			symbolTable = lexed.returnTable()
		except IOError as e:
			print("Error: No file in directory found")
	else:
		print("Error: No file arguments")
if __name__ == "__main__":
	main()
