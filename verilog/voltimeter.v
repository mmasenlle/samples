module voltimeter (clk,b,rx,ps2,seg,sen,bp1,tx,outs,ad,irda,vga);

input clk;
input wire [3:0] b;
input rx;
input wire [1:0] ps2;
output wire [7:0] seg;
output wire [3:0] sen;
output reg bp1;
output tx;
output outs;
inout wire [2:0] ad;
input irda;
output wire [4:0] vga;

reg [15:0] disp_data = 0;
reg [3:0] pts = 0;
reg [1:0] mode = 0;

wire ad_recv_end;
wire [7:0] ad_data;



always begin
	disp_data[7:0] = ad_data;
end


reg [31:0] cnt = 0;
always @ (posedge clk) cnt = cnt + 1'b1;
assign ad[0] = cnt[12];
assign ad[2] = !(cnt[16] && cnt[15]);

reg [7:0] sending_data = 8'd101;
always @ (posedge ad[2]) begin
	sending_data = ad_data;
end

assign outs = cnt[24];

uart_send us(clk,!ad[2],sending_data,tx);

ad_recv adr(clk,ad,ad_data,ad_recv_end);

display1 disp1(clk,disp_data,pts,mode,seg,sen);

endmodule
