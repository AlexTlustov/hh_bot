import asyncio
from telegram.ext import *
from hh_bot.command import *

from settings import KEY_BOT


VIDEO_SELECTION, PLIST_SELECTION, CITY_SELECTION, START_STATE = range(4)


def main():
    application = Application.builder().token(KEY_BOT).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_STATE: [CallbackQueryHandler(button_handler)],
            CITY_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, city_weather),
                MessageHandler(filters.LOCATION, location_weather)
            ],
            PLIST_SELECTION: [
                MessageHandler(filters.TEXT, add_plist)
            ],
            VIDEO_SELECTION: [
                MessageHandler(filters.TEXT, add_show)
            ]
            },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('test', test))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cancel', cancel))
    
    application.run_polling()



if __name__ == '__main__':
    asyncio.run(main())


# START_STATE: [CallbackQueryHandler(button_handler)], MessageHandler(filters.TEXT & ~filters.COMMAND, start)]