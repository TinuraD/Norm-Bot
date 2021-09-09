def normbot_more_callback(update, context):
    query = update.callback_query
    if query.data == "moretools_":
        query.message.edit_text(
            text=f"හායි, මම"
            f"\n\n මට පුළුවන් අනිත් බොට්ල වගේම Group Manage කරන්න. ඒ වගේම ඊටත් වඩා තවත් Features ගණනාවක් මට තියෙන්වා. පහළ Buttons වලින් තවත් විස්තර දැන ගන්න පුළුවන්.",
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
        )
