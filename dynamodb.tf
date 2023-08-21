resource "aws_dynamodb_table" "player_table" {
    name = "${var.prefix}_player_table"
    billing_mode = "PROVISIONED"
    read_capacity= "1"
    write_capacity= "1"
    
    hash_key = "id"
    
    attribute {
        name = "id"
        type = "S"
    }
}

resource "aws_dynamodb_table" "game_table" {
    name = "${var.prefix}_game_table"
    billing_mode = "PROVISIONED"
    read_capacity= "1"
    write_capacity= "1"
    
    hash_key = "id"
    
    attribute {
        name = "id"
        type = "S"
    }
}

resource "aws_dynamodb_table" "hand_table" {
    name = "${var.prefix}_hand_table"
    billing_mode = "PROVISIONED"
    read_capacity= "1"
    write_capacity= "1"
    
    hash_key = "id"
    
    attribute {
        name = "id"
        type = "S"
    }
}

resource "aws_dynamodb_table" "state_table" {
    name = "${var.prefix}_state_table"
    billing_mode = "PROVISIONED"
    read_capacity= "1"
    write_capacity= "1"
    
    hash_key = "id"
    
    attribute {
        name = "id"
        type = "S"
    }
}