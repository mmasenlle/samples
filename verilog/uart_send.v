module uart_send (clk,start,data,tx);

input clk, start;
input wire [7:0] data;
output reg tx = 1;

reg [31:0] cnt;
reg [7:0] dat;
reg [3:0] state = 9;
reg start_latch;

always @ (posedge clk) begin
	if (start && !start_latch) begin
		dat = data;
		//dat = 8'h41;
		state = 0;
		cnt = 0;
	end
	start_latch = start;
	if (state == 0) begin
		if (cnt > 5333) begin
			state = 4'd1;
			cnt = 0;
		end else tx = 0;
	end else if (state < 9) begin
		if (cnt > 5200) begin
			state = state + 4'd1;
			cnt = 0;
		end else tx = dat[state-1];
	end else tx = 1;
	cnt = cnt + 1;
end

endmodule
