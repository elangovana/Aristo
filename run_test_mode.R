input_test_file="../inputdata/validation_set.tsv"
rows_in_train = c(1:100)

source("./aristo_data.R")
test_data <- aristo_data(input_test_file, rows_in_train)


summary(test_data)