aristo_data <- function(aristo_file, rows_to_include=NULL){
  
  dataset <- read.csv(aristo_file, row.names="id", sep="\t", header=T, na.strings=c(""), as.is=c("question","answerA",  "answerB",	"answerC",	"answerD"))
  
  #if only specific rows have to extracted
  if ( !is.null(rows_to_include)){
    dataset <- dataset[rows_to_include, ]
  }
  
  #separate out y cols
  ycolnames <- c("correctAnswer")
  input <- dataset[, !colnames(dataset) %in%  ycolnames]
  colnames(input) <- c("question", "A", "B", "C", "D")
  
  out <- list(input = input ,                       
              y = if(sum(!is.na(dataset[, ycolnames]))!=0){ dataset[, ycolnames]} else{ NULL }
             )
  
  class(out) <- "aristo_data"  
  invisible(out)
}

print.aristo_data <- function(object){
  print("-- input data structure--")
  print(str(object$input))
  print("-- input data head--")
  print(head(object$input))
  print("--y cols- structure-")
  print(str(object$y))
  print("--y head--")
  print(dim(object$y))
}

summary.challenge_data <- function(object){
  print("-- input data dim --")
  print(dim(object$input))
  print("--y cols dim--")
  print(dim(object$y))
}

