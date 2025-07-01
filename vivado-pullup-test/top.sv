module top(
    input clk,
    inout test
);
    
    integer counter;
    logic test_en;
    
    assign test = test_en ? 'b0 : 'bz;
    
    always_ff @(posedge clk) begin
        if (counter >= 'h100000) begin
            counter <= 'b0;
        end
        else begin
            counter <= counter + 'b1;
        end
    end
    
    always_comb begin
        test_en = (counter <= 'h80000);      
    end

endmodule
