module display1 (clk,data,pts,mode,seg,sen);
input clk;
input wire [15:0] data;
input wire [3:0] pts;
input [1:0] mode;
output reg [7:0] seg = 8'b11111111;
output reg [3:0] sen = 4'b1111;

//wire [15:0] data;
//wire [3:0] pts;

//reg [7:0] seg = 8'b11111111;
//reg [3:0] sen = 4'b1111;

reg [15:0] number;
reg [3:0] points;

reg [23:0] cnt = 0;

wire [6:0] kb_s7_0;
wire [6:0] kb_s7_1;

function automatic [3:0] sel_s7;
 input [1:0] pos;
 begin
case(pos)
0: sel_s7 = 4'b0111;
1: sel_s7 = 4'b1101;
2: sel_s7 = 4'b1011;
3: sel_s7 = 4'b1110;
endcase
 end
endfunction

function automatic [6:0] set_s7c;
 input [7:0] val;
 begin
case(val)
65: set_s7c = 7'b1110111; //A

default: set_s7c = 0;
endcase
 end
endfunction

function automatic [6:0] set_s7;
 input [3:0] dig;
 begin
case(dig[3:0])
0: set_s7 = 7'b0111111;
1: set_s7 = 7'b0000110;
2: set_s7 = 7'b1011011;
3: set_s7 = 7'b1001111;
4: set_s7 = 7'b1100110;
5: set_s7 = 7'b1101101;
6: set_s7 = 7'b1111101;
7: set_s7 = 7'b0000111;
8: set_s7 = 7'b1111111;
9: set_s7 = 7'b1100111;
10: set_s7 = 7'b1110111; //A
11: set_s7 = 7'b1111100; //b
12: set_s7 = 7'b0111001; //C
13: set_s7 = 7'b1011110; //d
14: set_s7 = 7'b1111001; //E
15: set_s7 = 7'b1110001; //F
default: set_s7 = 0;
endcase
 end
endfunction


kb_to_s7 ks0(clk,data[7:0],kb_s7_0);
kb_to_s7 ks1(clk,data[15:8],kb_s7_1);

always @(posedge clk) cnt = cnt + 1'b1;
always @ (data) number = data;
always @ (pts) points = pts;

always @ (cnt[16]) begin
if (mode == 3) begin // kb
case(cnt[17:16])
0: begin
sen = sel_s7(0);
seg = kb_s7_0;
seg[7] = points[0];
end
1: begin
sen = sel_s7(1);
seg = kb_s7_1;
seg[7] = points[1];
end
2: begin
sen = sel_s7(0);
seg = 0;
seg[7] = points[2];
end
3: begin
sen = sel_s7(1);
seg = 0;
seg[7] = points[3];
end
endcase
end else if (mode == 2) begin // char
case(cnt[17:16])
0: begin
sen = sel_s7(0);
seg = set_s7c(number[7:0]);
seg[7] = points[0];
end
1: begin
sen = sel_s7(1);
seg = set_s7c(number[15:8]);
seg[7] = points[1];
end
2: begin
sen = sel_s7(0);
seg = set_s7c(number[7:0]);
seg[7] = points[2];
end
3: begin
sen = sel_s7(1);
seg = set_s7c(number[15:8]);
seg[7] = points[3];
end
endcase
end else if (mode == 1) begin // hex
case(cnt[17:16])
0: begin
sen = sel_s7(0);
seg = set_s7(number[3:0]);
seg[7] = points[0];
end
1: begin
sen = sel_s7(1);
seg = set_s7(number[7:4]);
seg[7] = points[1];
end
2: begin
sen = sel_s7(2);
seg = set_s7(number[11:8]);
seg[7] = points[2];
end
3: begin
sen = sel_s7(3);
seg = set_s7(number[15:12]);
seg[7] = points[3];
end
endcase
end
else begin // number
case(cnt[17:16])
0: begin
sen = sel_s7(0);
seg = set_s7(number % 10);
seg[7] = points[0];
end
1: begin
sen = sel_s7(1);
seg = set_s7((number/10) % 10);
seg[7] = points[1];
end
2: begin
sen = sel_s7(2);
seg = set_s7((number/100) % 10);
seg[7] = points[2];
end
3: begin
sen = sel_s7(3);
seg = set_s7((number/1000) % 10);
seg[7] = points[3];
end
endcase
end
end

endmodule