function addSelect() {
  $("#container-select").append("<select name='exercises' style='margin-left:120px;margin-top:15px'><option value=''>-- 운동 선택 --<option value='lunge'>Lunge</option><option value='push up'>Push Up</option><option value='shoulder press'>Shoulder Press</option>");
  $("#container-select").append("<select name='num' style='margin-left:4px'><option value=''>횟수</option><option value='5'>05</option><option value='10'>10</option><option value='15'>15</option><option value='20'>20</option>");
  $("#container-select").append("<select name='set' style='margin-left:4px'><option value=''>세트</option><option value='1'>1</option><option value='2'>2</option><option value='3'>3</option><option value='4'>4</option><option value='5'>5</option>");
}

function getSelect() {
  var _exercise_name = $("select[name=exercises] option:selected").text(); 
  var _number = $("select[name=num] option:selected").text(); 
  var _set_num = $("select[name=set] option:selected").text(); 

  var _exercise
  var first_letter = _exercise_name.slice(0,1)
  if (first_letter == "S") {
    _exercise = "shoulderpress"
  }else if (first_letter == 'L') {
    _exercise = 'lunge'
  }else {
    _exercise = 'pushup'
  }


  $.ajax({
    url : '/select/dataloading',
    type : 'POST',
    data : {exercise_name: _exercise_name, num: _number, set_num: _set_num},
    
    success: function (response) {
      console.log('성공쓰');
      window.location.href = '/exercise/'+ _exercise;
    },
    
    error : function (error) {
      console.log('실패쓰');
    }
  });
}
