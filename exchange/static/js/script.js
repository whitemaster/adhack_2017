$(document).ready(function () {
    $(".open-check").on("click", function(){
       if ($(this).attr('checked')) {
           // Если пора чекать - чекаем
           console.log('checking');
           $(this).removeClass('checked');
           $(this).text( $(this).attr('text'));

           //Вызываем like_checking если проверка засчитана - перечисляем деньги
           var id = $(this).attr('id');
           var user_id = $(this).attr('user_id');
           var block = $(this).parent();
           $.get('/task_check/'+id+'/'+user_id, function( data ){
               if (data == '1'){
                   // Пользователь выполнил задание, скроем его, пересчитаем баланс на сервере
                   block.hide();
               }
           });

           $(this).attr("checked", null);
       }else
       {
           console.log('open');
           // Открываем окно с постом
           popupWin = window.open(this.href, 'contacts', 'location,width=800,height=800,top=0');
           popupWin.focus();
           // Меняем кнопку
           $(this).addClass('checked');
           $(this).attr('text', $(this).text());
           $(this).text("Проверить");

           $(this).attr('checked','check');
       }
       return false;
    });
});