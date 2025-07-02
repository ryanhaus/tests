module top(
	input clk,
	input rst,
	inout updi
);

	localparam DB_MS = 50;
	localparam UART_CLK_FREQ = 57600;

	localparam CLK_FREQ = 100000000;
	localparam DB_CLK = DB_MS * CLK_FREQ / 1000;
	localparam UART_CLK_DIV = CLK_FREQ / UART_CLK_FREQ;

	logic [7:0] uart_tx_fifo_data, uart_rx_fifo_data;
	logic uart_tx_fifo_wr_en, uart_tx_fifo_full,
		uart_rx_fifo_rd_en, uart_rx_fifo_empty, rx_error,
		double_break_start, double_break_busy, double_break_done;

	updi_phy #(
		.UART_FIFO_DEPTH(16),
		.DOUBLE_BREAK_PULSE_CLK(DB_CLK),
		.UART_CLK_DIV(UART_CLK_DIV)
	) phy_inst (
		.clk(clk),
		.rst(rst),

		.uart_tx_fifo_data(uart_tx_fifo_data),
		.uart_tx_fifo_wr_en(uart_tx_fifo_wr_en),
		.uart_tx_fifo_full(uart_tx_fifo_full),

		.uart_rx_fifo_data(uart_rx_fifo_data),
		.uart_rx_fifo_rd_en(uart_rx_fifo_rd_en),
		.uart_rx_fifo_empty(uart_rx_fifo_empty),
		.rx_error(rx_error),

		.double_break_start(double_break_start),
		.double_break_busy(double_break_busy),
		.double_break_done(double_break_done),

		.updi(updi)
	);

	logic [7:0] counter;

	always_ff @(posedge clk) begin
		if (rst) begin
			counter <= 'b0;
		end
		else if (!uart_tx_fifo_full) begin
			counter <= counter + 'b1;
		end
	end

	always_comb begin
		uart_tx_fifo_wr_en = 'b0;

		if (!uart_tx_fifo_full) begin
			uart_tx_fifo_data = counter;
			uart_tx_fifo_wr_en = 'b1;
		end
	end

endmodule
