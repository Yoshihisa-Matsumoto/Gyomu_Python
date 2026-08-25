# Gitブランチ作成

git switch -c ＜新ブランチ名＞

# GitHubでマージ終わったら

1. git statusで未コミットないことの確認
2. git checkout main
3. git pull origin main

# Localの不要ブランチ削除

1. git branch -d <不要ブランチ名>
2. git push origin --delete <不要ブランチ名>

## 一括で不要ブランチ削除

- git branch --merged main | grep -v "main" | xargs git branch -d

## GitHub上の不要ブランチ削除

- git push origin --delete <不要ブランチ名>

# Git Branchを途中から作る場合

## （コミット前）

1. git switch -c <新ブランチ名>

## すでにコミットしている場合

1. git switch -c <新ブランチ名>
2. git switch main
3. git reset --hard origin/main

## Packaging まで (beta)

1. 必要ならブランチ作業
2. 開発
3. pnpm changeset でコミットメッセージのようなものを用意しておく
4. git commit
5. npm whoami でLoginされていることを確認。されてなければnpm login
6. pnpm release:beta

## Packaging まで

1. 必要ならブランチ作業
2. 開発
3. pnpm changeset でコミットメッセージのようなものを用意しておく
4. git commit
5. npm whoami でLoginされていることを確認。されてなければnpm login
6. pnpm release
