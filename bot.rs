use serenity::{
    async_trait,
    model::{channel::Message, gateway::Ready},
    prelude::*,
};
use std::fs::File;
use std::io::{BufRead, BufReader};

struct Handler;

impl EventHandler for Handler {
    fn ready(&self, ctx: Context, _: Ready) {
        println!("Connected as {}", ctx.user.name);
    }

    async fn message(&self, ctx: Context, msg: Message) {
        if msg.author.bot || msg.is_private() {
            return;
        }

        if msg.content.starts_with("~") {
            if let Err(why) = msg.delete(&ctx).await {
                eprintln!("Error deleting message: {:?}", why);
            }
            return;
        }

        let profanity_list = read_profanity_list().await;
        for word in profanity_list.iter() {
            let regex_pattern = format!(r"\b\w*{}\w*\b", regex::escape(word));
            let regex_match = regex::Regex::new(&regex_pattern)
                .unwrap()
                .find(&msg.content);

            if let Some(_) = regex_match {
                let filtered_word = format!("{}{}{}", &word[..1], "*".repeat(word.len() - 2), &word[word.len() - 1..]);
                let filtered_message = regex::Regex::new(&regex_pattern)
                    .unwrap()
                    .replace_all(&msg.content, &filtered_word[..]);

                let user = msg.author.mention();
                if let Err(why) = msg.channel_id.say(&ctx.http, format!("{}: {}", user, filtered_message)).await {
                    eprintln!("Error sending message: {:?}", why);
                }
                if let Err(why) = msg.delete(&ctx).await {
                    eprintln!("Error deleting message: {:?}", why);
                }
                break;
            }
        }
    }
}

async fn read_profanity_list() -> Vec<String> {
    let file = File::open("profanity.txt").unwrap();
    let reader = BufReader::new(file);

    reader.lines().map(|line| line.unwrap().trim().to_string()).collect()
}

#[tokio::main]
async fn main() {
    let token = "#redacted".to_string();

    let mut client = Client::builder(&token)
        .event_handler(Handler)
        .await
        .expect("Error creating client");

    if let Err(why) = client.start().await {
        eprintln!("Error starting client: {:?}", why);
    }
}
