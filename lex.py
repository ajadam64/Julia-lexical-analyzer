class lex:
	
	#token declarations and opcode initilization
	EOF, ID, LITERAL_INTEGER, ASSIGNMENT_OPERATOR, LE_OPERATOR, LT_OPERATOR, GE_OPERATOR, GT_OPERATOR, \
	EG_OPERATOR, NE_OPERATOR, ADD_OPERATOR, SUB_OPERATOR, MUL_OPERATOR, DIV_OPERATOR, MOD_OPERATOR, LEFT_PAREN, RIGHT_PAREN, \
	IF_KEYWORD, THEN_KEYWORD, ELSE_KEYWORD, END_KEYWORD, WHILE_KEYWORD, DO_KEYWORD, FUNCTION_KEYWORD, PRINT_KEYWORD = range(25)
	
	#token sring names
	sym = ["END_OF_FILE", "ID", "LITERAL_INTEGER", "ASSIGNMENT_OPERATOR", "LE_OPERATOR", "LT_OPERATOR", "GE_OPERATOR", "GT_OPERATOR", 
		"EG_OPERATOR", "NE_OPERATOR", "ADD_OPERATOR", "SUB_OPERATOR", "MUL_OPERATOR", "DIV_OPERATOR", "MOD_OPERATOR", "LEFT_PAREN", "RIGHT_PAREN",
		"IF_KEYWORD", "THEN_KEYWORD", "ELSE_KEYWORD", "END_KEYWORD", "WHILE_KEYWORD", "DO_KEYWORD", "FUNCTION_KEYWORD", "PRINT_KEYWORD"]
	
	#one character only with no combined tokens, no division because '/' can be paired with '/' so must be handeled sperately
	singleSym = {'+': ADD_OPERATOR, '-': SUB_OPERATOR, '*': MUL_OPERATOR, '%': MOD_OPERATOR, '(': LEFT_PAREN, ')': RIGHT_PAREN}
	
	#special language keywords
	keywords = {'if': IF_KEYWORD, 'then': THEN_KEYWORD, 'else': ELSE_KEYWORD, 'end': END_KEYWORD, 'while': WHILE_KEYWORD, 'do': DO_KEYWORD, 'function': FUNCTION_KEYWORD, 'print': PRINT_KEYWORD}
		
	source = None #Source file (in bytes not string)
	char = " " #Char read from source file
	pos = 0 #Position of character in a line
	line = 1 #Line in source file
	
	lex = [] #Storage of lexeme, token, opcode, line, and position
	
	#print error showing where in the source code file it is located
	def err(self, err, line, pos):
		print("Error: %s, Line: %d, Position: %d" % (err, line, pos))
		self.source.seek(0) #Must move the read cursor back to the beginning of the file
		print(self.source.readlines()[line - 1].strip())
		for i in range(pos):
			if i == pos - 1:
				print("^", end="")
			else:
				print("-", end="")
		print()
		quit() #Exit
		
	#Gets the next character in the source file
	def getChar(self):
		self.char = self.source.read(1) #Decodes next bytes into one unicode character
		self.pos += 1 #Must update the position if our character scince it's new
		if self.char == '\n': #New line so must
			self.pos = 0
			self.line += 1
		if self.char == '\t': #.isspace does not check for tabs
			self.pos = 0
		return self.char
			
	#Gets a token for a divion symbol or skips comment lines
	def divideOrComment(self, errline, errpos):
		if self.getChar() != '/':
			return [self.DIV_OPERATOR, errline, errpos, "/"]
		else: #there is a //comment, then skip the rest of the file line
			while True:
				if len(self.char) == 0:
					self.err("End of file in comment", errline, errpos)
				elif self.char == '\n':
					return self.getToken() #gets the next character's token in the next line
				self.getChar()
				
	#Gets token for Integer or Identifier or Keyword
	def intIdKeyword(self, errline, errpos):
		isNumber = True
		lexeme = ""
		
		#moves through characters to check if they are digits, if one is not a digit then they all aren't digits 
		while self.char.isalnum():
			lexeme += self.char
			if not self.char.isdigit():
				isNumber = False
			self.getChar()
			
		#Check for characters that do not belong in julia
		if len(lexeme) == 0: 
			self.err("Unknown Character", errline, errpos)
		elif lexeme[0].isdigit(): 
			#cannot have a number as first char in lexeme
			if not isNumber: 
				self.err("No IDs with starting integers allowed (%s)" % (lexeme), errline, errpos)
			else: 
				#If the lexeme is a number return a integer token
				return [self.LITERAL_INTEGER, errline, errpos, lexeme]
		#Checks for keywords and returns correct token in the keyword dictionary
		elif lexeme in self.keywords: 
			return [self.keywords[lexeme], errline, errpos, lexeme]
		else: 
			return [self.ID, errline, errpos, lexeme]
	
	#Gets a combined operator's token if the next character is equal to a known compatable character
	def pairOperators(self, knownChar, withPairToken, withoutPairToken, errline, errpos):
		lexeme = self.char
		#If the next character is equal to the exepected character then we return the token of both the characters paired
		if self.getChar() == knownChar:
			self.getChar()
			lexeme += knownChar
			return [withPairToken, errline, errpos, lexeme]
		#This is for when you only want a pair and not a single character. Ex: ~= but not ~
		elif withoutPairToken == self.EOF:
			self.err("Invalid Character", errline, errpos)
		else:
			#If current char and knownChar are not a pair and not only a pair then we return the single character's token
			return [withoutPairToken, errline, errpos, lexeme]
	
	#Combs through whitespace to find a non space character
	def getNonBlank(self):
		while self.char.isspace():
			self.getChar()
	
	#Checks current character for the correct token
	def getToken(self):
		self.getNonBlank()
		
		ch = self.char
		errline = self.line
		errpos = self.pos
		
		if len(ch) == 0: return [self.EOF, errline, errpos, ""]
		elif ch == '/': return self.divideOrComment(errline, errpos)
		elif ch == '=': return self.pairOperators('=', self.EG_OPERATOR, self.ASSIGNMENT_OPERATOR, errline, errpos)
		elif ch == '~': return self.pairOperators('=', self.NE_OPERATOR, self.EOF, errline, errpos)
		elif ch == '<': return self.pairOperators('=', self.LE_OPERATOR, self.LT_OPERATOR, errline, errpos)
		elif ch == '>': return self.pairOperators('=', self.GE_OPERATOR, self.GT_OPERATOR, errline, errpos)
		elif ch in self.singleSym:
			singleSymbolToken = self.singleSym[ch]
			self.getChar()
			return [singleSymbolToken, errline, errpos, ch]
		else: return self.intIdKeyword(errline, errpos)
		
	#Returns the full table(list) for the parser to process
	def returnTable(self):
		return self.lex
		
	#prints the source file and outputs the correct full table of tokens, lexems, opcode, line, and position of a source file
	def printTable(self):
		self.source.seek(0)
		print(self.source.read())
		print("_" * 92)
		print("%-20s %-20s %-20s %-20s %-20s" % ("Lexeme", "Token", "Opcode", "Line", "Position"))
		print("_" * 92, "\n")
		count = 0
		while True:
			token = self.lex[count][0]
			line = self.lex[count][1]
			pos = self.lex[count][2]
			lexeme = self.lex[count][3]
			count += 1
			
			print("%-20s %-20s %-20d %-20d %-20d" % (str(lexeme), self.sym[token], token, line, pos))
			
			if token == self.EOF:
				break
		print()

	#Initialize the lexical analyzer by getting tokens for each lexeme, when done the last character in the file will not have a length because it is null and its token will be EOF
	def __init__(self, source):
		self.source = source
		
		count = 0
		while True:	
			self.lex += [self.getToken()]
			token = self.lex[count][0]
			count += 1
			if token == self.EOF:
				break

