module ad_recv (clk,ad,data,endb);

input clk;
input [2:0] ad; // adcsn, addat, adclk
output reg [7:0] data = 8'd100;
output reg endb;

//reg [31:0] cnt;
reg [3:0] state = 4'd10;
reg cs_latch = 1;

always @ (posedge ad[0]) begin
	if (!ad[2] && cs_latch) begin
		state = 0;
		endb = 0;
	end
	cs_latch = ad[2];
	if (!ad[2] && state < 8) begin
		data[7 - state] = ad[1];
		state = state + 4'd1;
		if (state == 8) endb = 1;
	end
end

endmodule
